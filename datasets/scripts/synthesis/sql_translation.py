from copy import deepcopy
from pathlib import Path

import sqlparse
from sqlparse import sql
import sqlglot
from sqlglot import dialects
import sqlglot.expressions as exp
from tqdm import tqdm
from joblib import Parallel, delayed

from common import load_json, save_json, SchemaTranslation
from common.sql import get_columns_names, get_tables_names
from common.constants import *


def translate_tables_list(tables, trans):
    translated_tables = deepcopy(tables)

    for db in tqdm(translated_tables, desc="Translating tables"):
        db_id = db["db_id"]

        # translate columns
        assert db["column_names"][0][1] == "*"
        assert db["column_names_original"][0][1] == "*"
        for i in range(1, len(db["column_names_original"])):
            table_idx, column_name_original = db["column_names_original"][i]
            table_name = db["table_names_original"][table_idx]
            columns_trans = trans[db_id][table_name][column_name_original]
            db["column_names_original"][i][1] = columns_trans.orig
            db["column_names"][i][1] = columns_trans.name

        # translate tables
        for i in range(len(db["table_names_original"])):
            table_name = db["table_names_original"][i]
            table_trans = trans[db_id][table_name]
            db["table_names_original"][i] = table_trans.orig
            db["table_names"][i] = table_trans.name
    
    return translated_tables


def translate_tables(trans, db_prefix, output_path):
    tables = load_json(BASE_PATH / "tables.json")
    
    if trans is not None:
        tables = translate_tables_list(tables, trans)
        
    for schema in tables:
        schema["db_id"] = f'{db_prefix}_{schema["db_id"]}'
        
    save_json(output_path, tables)


def get_tables_aliasing(sql):
    parsed = sqlglot.parse_one(sql)
    aliasing = [
        (table.this.output_name, table.alias)
        for table in parsed.find_all(exp.Table)
        if table.alias
    ]
    return aliasing


def split_nested_query(tokens):
    outer_query = []
    active_nested_query = []
    all_nested_queries = []

    is_in_nested_query = False
    parenth_level = 0

    for i in range(len(tokens)):
        token = tokens[i]

        if str(token) == "(":
            parenth_level += 1

        elif str(token) == ")":
            parenth_level -= 1

            if parenth_level == 0 and is_in_nested_query:
                all_nested_queries.append(active_nested_query)
                active_nested_query = []
                is_in_nested_query = False

                # insert 'select 1' to make outer query valid
                outer_query.extend(
                    [sql.Token("fake", "select"), sql.Token("fake", "1")]
                )

        elif str(token).upper() == "SELECT":
            if parenth_level == 1 and i > 0 and str(tokens[i - 1]) == "(":
                is_in_nested_query = True

        if is_in_nested_query:
            active_nested_query.append(token)
        else:
            outer_query.append(token)

    return outer_query, all_nested_queries


def split_set_query(tokens):
    active_query = []
    queries = []
    parenth_level = 0

    for i in range(len(tokens)):
        token = tokens[i]

        if str(token) == "(":
            parenth_level += 1

        elif str(token) == ")":
            parenth_level -= 1

        if (
            str(token).upper() in ["UNION", "EXCEPT", "INTERSECT"]
            and parenth_level == 0
        ):
            queries.append(active_query)
            active_query = []
        else:
            active_query.append(token)

    queries.append(active_query)
    return queries


def get_token_type(tokens, token):
    MODIFIED_TEXT_TOKEN = "very_uncommon_token_AgDFwerSdrwRewJh"

    before_query = " ".join([str(token) for token in tokens])
    initial_value = token.value
    token.value = MODIFIED_TEXT_TOKEN
    after_query = " ".join([str(token) for token in tokens])
    token.value = initial_value

    before_parsed = sqlglot.parse_one(before_query, dialect=dialects.SQLite)

    try:
        after_parsed = sqlglot.parse_one(after_query, dialect=dialects.SQLite)
    except Exception:
        return "other"

    before_columns = get_columns_names(before_parsed)
    after_columns = get_columns_names(after_parsed)

    before_tables = get_tables_names(before_parsed)
    after_tables = get_tables_names(after_parsed)

    if (
        token.value in before_columns
        and MODIFIED_TEXT_TOKEN in after_columns
        and len(after_columns) == len(before_columns)
    ):
        return "column"
    elif token.value in before_tables and MODIFIED_TEXT_TOKEN in after_tables:
        return "table"
    else:
        return "other"


def translate_simple_query(
    tokens, db_id, trans, parent_aliasing=None
):
    trans = trans[db_id]

    query = " ".join([str(token) for token in tokens])
    tables_names = get_tables_names(query)
    tables_names_low = [name.lower() for name in tables_names]

    parent_aliasing = parent_aliasing or []
    this_aliasing = get_tables_aliasing(query)
    this_aliasing_rev = {new.lower(): old for old, new in this_aliasing}
    parent_aliasing_rev = {new.lower(): old for old, new in parent_aliasing}
    aliasing_rev = {**parent_aliasing_rev, **this_aliasing_rev}

    for i in reversed(range(len(tokens))):
        token_type = get_token_type(tokens, tokens[i])
        token = str(tokens[i])
        token_low = token.lower()

        if token_type == "column":
            table_name = (
                str(tokens[i - 2]) if i >= 2 and str(tokens[i - 1]) == "." else None
            )

            if table_name is None:
                possible_table_names = [
                    table_name
                    for table_name, table_trans in trans.tables.items()
                    if table_name in tables_names_low and token_low in table_trans.columns_names
                ]
                assert len(possible_table_names) == 1
                table_name = possible_table_names[0]

            elif table_name.lower() in aliasing_rev:
                table_name = aliasing_rev[table_name.lower()]

            trans_name = trans[table_name][token_low].orig
            trans_name_in_style = copy_name_style(token, trans_name)
            tokens[i].value = trans_name_in_style

        elif token_type == "table" and token_low not in aliasing_rev:
            trans_name = trans[token_low].orig
            trans_name_in_style = copy_name_style(token, trans_name)
            tokens[i].value = trans_name_in_style

    return this_aliasing


def copy_name_style(style, name):
    # make lower if style is lower
    if style == style.lower():
        return name.lower()
    
    # make upper if style is upper
    if style == style.upper():
        return name.upper()
    
    style_space = style.replace('_', ' ')
    
    # make titled if style is titled
    if style_space == style_space.title():
        return name.replace('_', ' ').title().replace(' ', '_')
    
    # if style not recognized
    return name


def translate_query_recursively(tokens, db_id, trans, aliasing):
    set_queries = split_set_query(tokens)
    for set_query in set_queries:
        outer_query, nested_queries = split_nested_query(set_query)

        outer_aliasing = translate_simple_query(
            outer_query, db_id, trans, aliasing
        )

        for query in nested_queries:
            translate_query_recursively(
                query, db_id, trans, [*aliasing, *outer_aliasing]
            )


def translate_query(query, db_id, trans):
    statement = sqlparse.parse(query)[0]
    tokens = [token for token in statement.flatten() if str(token).strip() != ""]
    translate_query_recursively(tokens, db_id, trans, [])
    return str(statement)


def translate_queries(samples, trans, query_lang):
    return Parallel(-1)(
        delayed(translate_queries_single)(sample, query_lang, trans)
        for sample in tqdm(samples, desc="Translating SQL queries")
    )


def translate_queries_single(sample, query_lang, trans):
    sample.query[query_lang] = translate_query(
        query=sample.query[query_lang], 
        db_id=sample.db_id,
        trans=trans
    )
    return sample
