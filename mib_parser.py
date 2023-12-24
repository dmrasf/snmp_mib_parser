import sys
from pyparsing import (
    DelimitedList,
    Keyword,
    Literal,
    Optional,
    ParseException,
    QuotedString,
    Word,
    ZeroOrMore,
    alphanums,
    alphas,
    nums,
    restOfLine,
)
from mib_generator import mib_generator


class mib_parse:
    def __init__(self) -> None:
        self.node_list = []
        self.node_dict = {}
        self.name_oid = {}

        self.bnf = self.smi_bnf()

    def add_node(self, node):
        """add_node"""
        self.node_list.append(node)
        node["kids"] = []
        oid = list(self.name_oid[node["parent_name"]])
        node["parent"] = tuple(oid)
        oid.append(int(node["subId"]))
        self.node_dict[tuple(oid)] = node
        self.name_oid[node["name"]] = tuple(oid)
        if node["parent"] in self.node_dict:
            parent = self.node_dict[node["parent"]]
            kid = (node["name"], node["type"], node["subId"], tuple(oid))
            parent["kids"].append(kid)

    def object_type_action(self, toks):
        """object_type_action"""
        node = toks.asDict()
        node["type"] = "object"

        if "syn_seq_of" in node.keys():
            node["type"] = "table"
        elif "index" in node.keys():
            node["type"] = "row"
        elif self.node_dict[self.name_oid[node["parent_name"]]]["type"] == "row":
            node["type"] = "column"
        elif self.node_dict[self.name_oid[node["parent_name"]]]["type"] == "ident":
            node["type"] = "scalar"
        self.add_node(node)

    def notify_type_action(self, toks):
        """notify_type_action"""
        node = toks.asDict()
        node["type"] = "notification"
        self.add_node(node)

    def object_identifier_action(self, toks):
        """object_identifier_action"""
        node = toks.asDict()
        node["type"] = "ident"
        if node["name"] in self.name_oid.keys():
            print(f"OBJECT IDENTIFIER: {node['name']} repeat!")
        else:
            self.add_node(node)

    def identity_action(self, toks):
        """identify_action"""
        node = toks.asDict()
        node["type"] = "ident"
        if node["name"] in self.name_oid.keys():
            print(f"MODULE-IDENTITY: {node['name']} repeat!")
        else:
            self.add_node(node)

    def enums_action(self, toks):
        """enums_action"""
        enum_value = "(" + Word(nums).set_results_name("enum_value") + ")"
        for i in range(1, len(toks.enums), 2):
            try:
                v = enum_value.parse_string(toks.enums[i])
                toks.enums[i] = v.enum_value
            except ParseException as _:
                pass

    def smi_bnf(self):
        """smi_bnf"""
        # punctuation
        # pylint: disable=unused-variable
        colon = Literal(":")
        lbrace = Literal("{")
        rbrace = Literal("}")
        lbrack = Literal("[")
        rbrack = Literal("]")
        lparen = Literal("(")
        rparen = Literal(")")
        equals = Literal("=")
        comma = Literal(",")
        dot = Literal(".")
        slash = Literal("/")
        bslash = Literal("\\")
        star = Literal("*")
        semi = Literal(";")
        langle = Literal("<")
        rangle = Literal(">")

        # keywords
        assign_ = Keyword("::=")
        define_ = Keyword("DEFINITIONS")
        begin_ = Keyword("BEGIN")
        end_ = Keyword("END")
        imports_ = Keyword("IMPORTS")
        from_ = Keyword("FROM")
        identity_ = Keyword("MODULE-IDENTITY")
        updated_ = Keyword("LAST-UPDATED")
        org_ = Keyword("ORGANIZATION")
        contact_ = Keyword("CONTACT-INFO")
        revision_ = Keyword("REVISION")
        descr_ = Keyword("DESCRIPTION")
        object_ = Keyword("OBJECT")
        objects_ = Keyword("OBJECTS")
        notify_type_ = Keyword("NOTIFICATION-TYPE")
        identifier_ = Keyword("IDENTIFIER")
        octet_ = Keyword("OCTET")
        string_ = Keyword("STRING")
        obj_type_ = Keyword("OBJECT-TYPE")
        syntax_ = Keyword("SYNTAX")
        units_ = Keyword("UNITS")
        access_ = Keyword("ACCESS")
        max_access_ = Keyword("MAX-ACCESS")
        status_ = Keyword("STATUS")
        reference_ = Keyword("REFERENCE")
        index_ = Keyword("INDEX")
        sequence_ = Keyword("SEQUENCE")
        of_ = Keyword("OF")
        size_ = Keyword("SIZE")

        identifier = Word(alphas + "-", alphanums + "-").set_name("identifier")
        text = QuotedString('"', multiline=True)
        sub_id = Word(nums)

        imports_list = DelimitedList(identifier)
        imports_item = imports_list + from_ + identifier
        # IMPORTS
        imports_def = imports_ + ZeroOrMore(imports_item) + semi

        # { enterprises 12345 }
        assignment = (
            lbrace
            + identifier.set_results_name("parent_name")
            + sub_id.set_results_name("subId")
            + rbrace
        )

        # suppress 只用来匹配，不作为结果输出
        updated = (updated_ + text).suppress()
        org = (org_ + text).suppress()
        contact = (contact_ + text).suppress()
        descr = (descr_ + text).suppress()
        reference = (reference_ + text).suppress()
        revision = (revision_ + text).suppress()
        revision_item = revision + descr

        identity_body = updated + org + contact + descr + ZeroOrMore(revision_item)
        # MODULE-IDENTITY
        identity_def = (
            identifier.set_results_name("name")
            + identity_
            + identity_body
            + assign_
            + assignment
        ).set_parse_action(self.identity_action)

        # OBJECT IDENTIFIER
        object_identifier = (
            identifier.set_results_name("name")
            + object_
            + identifier_
            + assign_
            + assignment
        ).set_parse_action(self.object_identifier_action)

        # 范围
        bounds = QuotedString("(", endQuoteChar=")").set_results_name("bounds")
        size_def = Word("(", max=1) + size_ + bounds + Word(")", max=1)
        # 枚举
        syntax_enum_item = identifier + Word("(" + nums + ")")
        syntax_enum = (
            lbrace
            + DelimitedList(syntax_enum_item)
            .set_results_name("enums")
            .set_parse_action(self.enums_action)
            + rbrace
        )

        syntax_opts = (syntax_enum | size_def | bounds).set_name("syntaxOpts")

        integer = identifier.set_results_name("syntax") + (Optional(syntax_opts))
        sequence_of = sequence_ + of_ + identifier.set_results_name("syn_seq_of")
        syn_obj_id = (object_ + identifier_).set_results_name("syntax")
        syn_octet_string = (
            octet_.set_results_name("syntax") + string_ + Optional(size_def)
        )
        syntax = syntax_ + (syn_obj_id | syn_octet_string | sequence_of | integer)
        units = units_ + text.set_results_name("units")
        access = (max_access_ | access_) + identifier.set_results_name("access")
        status = status_ + identifier
        index_def = (
            index_
            + lbrace
            + DelimitedList(identifier).set_results_name("index")
            + rbrace
        )

        object_body = (
            syntax
            + Optional(units)
            + access
            + status
            + Optional(descr)
            + Optional(reference)
            + Optional(index_def)
        )
        # OBJECT-TYPE
        object_type = (
            identifier.set_results_name("name")
            + obj_type_
            + object_body
            + assign_
            + assignment
        ).set_parse_action(self.object_type_action)

        # TABLE ENTRY
        sequence_def = (
            identifier
            + assign_
            + sequence_
            + QuotedString("{", multiline=True, endQuoteChar="}")
        )

        nofify_objects = (
            objects_
            + lbrace
            + DelimitedList(identifier).set_results_name("objects")
            + rbrace
        )
        notify_body = nofify_objects + Optional(access) + status + Optional(descr)
        # NOTIFICATION-TYPE
        notify_type = (
            identifier.set_results_name("name")
            + notify_type_
            + notify_body
            + assign_
            + assignment
        ).set_parse_action(self.notify_type_action)

        # textualConv = (
        #     (
        #         lineStart
        #         + identifier
        #         + White()
        #         + assign_
        #         + White()
        #         + OneOrMore(Word(alphas) + White(" \t"))
        #         + lineEnd
        #     )
        #     .leaveWhitespace()
        #     .setDebug()
        # )
        module_item = (
            imports_def
            | identity_def
            | object_identifier
            | object_type
            | sequence_def
            | notify_type
        )
        module_def = (
            identifier + define_ + assign_ + begin_ + ZeroOrMore(module_item) + end_
        )

        bnf = module_def

        single_line_comment = "--" + restOfLine
        bnf.ignore(single_line_comment)

        return bnf

    def parse(self, fname):
        """parse"""
        private = {
            "subId": 4,
            "type": "ident",
            "name": "private",
            "parent": (1, 3, 6, 1),
            "kids": [("enterprises", "ident", "1")],
        }
        enterprises = {
            "subId": 1,
            "type": "ident",
            "name": "enterprises",
            "parent": (1, 3, 6, 1, 4),
            "kids": [],
        }
        self.node_dict[(1, 3, 6, 4)] = private
        self.node_dict[(1, 3, 6, 4, 1)] = enterprises
        self.name_oid["enterprises"] = (1, 3, 6, 4, 1)
        self.name_oid["private"] = (1, 3, 6, 4)
        self.node_list.append(private)
        self.node_list.append(enterprises)

        try:
            self.bnf.parse_file(fname)
            self.node_list.reverse()
            print("Parsing of " + fname + " complete.")

            gen = mib_generator(self.node_list, self.node_dict, fname)
            gen.process()
        except ParseException as err:
            print(err.line)
            print(" " * (err.column - 1) + "^")
            print(err)
        except IOError as _:
            print("could not open input mib file " + fname)
        finally:
            pass


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        print("usage: mibparser.py <mib-file>")
    else:
        parse = mib_parse()
        parse.parse(args[0])
