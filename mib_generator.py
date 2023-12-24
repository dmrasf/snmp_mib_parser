class mib_generator:
    def __init__(self, nodelist, nodedict, fname):
        """Constructor for the MibGenerator class
        converts the input filename to the output filename
        opens the output file
        writes some prelude code to the output file
        """
        self.node_list = nodelist
        self.node_dict = nodedict
        self.syntax_dict = {
            "integer": "SNMP_ASN1_TYPE_INTEGER",
            "integer32": "SNMP_ASN1_TYPE_INTEGER",
            "octet": "SNMP_ASN1_TYPE_OCTET_STRING",
            "displaystring": "SNMP_ASN1_TYPE_OCTET_STRING",
            "object": "SNMP_ASN1_TYPE_OBJECT_ID",
            "timeticks": "SNMP_ASN1_TYPE_TIMETICKS",
            "gauge": "SNMP_ASN1_TYPE_GAUGE",
            "gauge32": "SNMP_ASN1_TYPE_GAUGE",
            "counter": "SNMP_ASN1_TYPE_COUNTER",
            "counter32": "SNMP_ASN1_TYPE_COUNTER",
            "ipaddress": "SNMP_ASN1_TYPE_IPADDRESS",
            "physaddress": "SNMP_ASN1_TYPE_OCTET_STRING",
            "networkaddress": "SNMP_ASN1_TYPE_IPADDRESS",
        }
        self.access_dict = {
            "read-only": "SNMP_NODE_INSTANCE_READ_ONLY",
            "read-write": "SNMP_NODE_INSTANCE_READ_WRITE",
            "write-only": "SNMP_NODE_INSTANCE_WRITE_ONLY",
            "not-access": "SNMP_NODE_INSTANCE_NOT_ACCESSIBLE",
        }

        self.fname = fname.split(".")[0].replace("-", "_")
        self.out_fname_c = self.fname + ".c"
        self.out_fname_h = self.fname + ".h"
        self.out_file_c = open(self.out_fname_c, "w", encoding="utf-8")
        self.node_extern = []
        self.func_extern = []
        self.out_file_c.write(f'#include "{self.out_fname_h}"')
        self.generate_empty_line(2)

    def get_datatype(self, syntax):
        dt = syntax.lower()
        if dt in self.syntax_dict.keys():
            return self.syntax_dict[dt]
        return "SNMP_ASN1_TYPE_INTEGER"

    def get_access(self, access):
        ac = access.lower()
        if ac in self.access_dict.keys():
            return self.access_dict[ac]
        return "SNMP_NODE_INSTANCE_NOT_ACCESSIBLE"

    def generate_empty_line(self, num):
        f = self.out_file_c
        for _ in range(num):
            f.write("\r\n")

    def generate_scalar_array_get_method(self, node):
        f = self.out_file_c
        self.func_extern.append(
            f"s16_t {node['name']}_get_value(const struct snmp_scalar_array_node_def *scalar, void *value);\r\n"
        )
        f.write(
            f"s16_t {node['name']}_get_value(const struct snmp_scalar_array_node_def *scalar, void *value)\r\n"
        )
        f.write("{\r\n")
        f.write("    switch (scalar->oid) {\r\n")
        for kid in node["kids"]:
            f.write(f"    case {kid[2]}: // {kid[0]}\r\n")
            f.write("        break;\r\n")
        f.write("    default:\r\n")
        f.write("        break;\r\n")
        f.write("    }\r\n")
        f.write("    return sizeof(*value);\r\n")
        f.write("}\r\n")
        f.write("\r\n")

    def generate_scalar_array_test_method(self, node):
        f = self.out_file_c
        self.func_extern.append(
            f"snmp_err_t {node['name']}_set_test(const struct snmp_scalar_array_node_def *scalar, u16_t len, void *value);\r\n"
        )
        f.write(
            f"snmp_err_t {node['name']}_set_test(const struct snmp_scalar_array_node_def *scalar, u16_t len, void *value)\r\n"
        )
        f.write("{\r\n")
        f.write("    snmp_err_t ret = SNMP_ERR_NOERROR;\r\n")
        f.write("    return ret;\r\n")
        f.write("}\r\n")
        f.write("\r\n")

    def generate_scalar_array_set_method(self, node):
        f = self.out_file_c
        self.func_extern.append(
            f"snmp_err_t {node['name']}_set_value(const struct snmp_scalar_array_node_def *scalar, u16_t len, void *value);\r\n"
        )
        f.write(
            f"snmp_err_t {node['name']}_set_value(const struct snmp_scalar_array_node_def *scalar, u16_t len, void *value)\r\n"
        )
        f.write("{\r\n")
        f.write("    snmp_err_t ret = SNMP_ERR_NOERROR;\r\n")
        f.write("    return ret;\r\n")
        f.write("}\r\n")
        f.write("\r\n")

    def generate_scalar_array(self, node):
        """生成array scalar"""
        print("scalar array: ", node["name"])
        f = self.out_file_c
        self.node_extern.append(
            f"extern const struct snmp_scalar_array_node {node['name']}_root;\r\n"
        )

        self.generate_scalar_array_get_method(node)
        self.generate_scalar_array_test_method(node)
        self.generate_scalar_array_set_method(node)
        f.write(
            f"static const struct snmp_scalar_array_node_def {node['name']}_nodes[] = {'{'}\r\n"
        )
        for kid in node["kids"]:
            f.write(
                f"    {'{'}{kid[2]}, {self.get_datatype(self.node_dict[kid[3]]['syntax'])}, {self.get_access(self.node_dict[kid[3]]['access']) }{'}'}, // {kid[0]}\r\n"
            )
        f.write("};\r\n")
        f.write(f"const struct snmp_scalar_array_node {node['name']}_root =\r\n")
        f.write(
            f"    SNMP_SCALAR_CREATE_ARRAY_NODE({node['subId']}, {node['name']}_nodes,\r\n"
        )
        f.write(f"                                  {node['name']}_get_value,\r\n")
        f.write(f"                                  {node['name']}_set_test,\r\n")
        f.write(f"                                  {node['name']}_set_value);\r\n")
        self.generate_empty_line(1)

    def generate_empty_tree(self, node):
        """生成empty tree"""
        print("empty tree: ", node["name"])
        f = self.out_file_c
        self.node_extern.append(
            f"extern const struct snmp_tree_node {node['name']}_root;\r\n"
        )
        f.write(
            f"static const struct snmp_node *const {node['name']}_nodes[] = {'{'}{'}'};\r\n"
        )
        f.write(
            f"const struct snmp_tree_node {node['name']}_root = SNMP_CREATE_EMPTY_TREE_NODE({node['subId']});\r\n"
        )
        self.generate_empty_line(1)

    def generate_tree(self, node):
        """生成tree"""
        print("tree: ", node["name"])
        f = self.out_file_c
        self.node_extern.append(
            f"extern const struct snmp_tree_node {node['name']}_root;\r\n"
        )
        f.write(
            f"static const struct snmp_node *const {node['name']}_nodes[] = {'{'}\r\n"
        )
        for kid in node["kids"]:
            if (
                self.is_array_of_scalar(self.node_dict[kid[3]]["kids"])
                or kid[1] == "scalar"
            ):
                f.write(f"    &{kid[0]}_root.node.node, // {kid[0]}\r\n")
            else:
                f.write(f"    &{kid[0]}_root.node, // {kid[0]}\r\n")
        f.write("};\r\n")
        f.write(
            f"const struct snmp_tree_node {node['name']}_root = SNMP_CREATE_TREE_NODE({node['subId']}, {node['name']}_nodes);\r\n"
        )
        self.generate_empty_line(1)

    def generate_scalar(self, node):
        """生成scalar"""
        print("scalar: ", node["name"])
        f = self.out_file_c
        self.node_extern.append(
            f"extern const struct snmp_scalar_node {node['name']}_root;\r\n"
        )
        f.write(
            f"const struct snmp_scalar_node {node['name']}_root = SNMP_SCALAR_CREATE_NODE({node['subId']}, {self.get_datatype(node['syntax'])}, {self.get_access(node['access'])}, NULL, NULL, NULL);\r\n"
        )
        self.generate_empty_line(1)

    def generate_column(self, node):
        """生成column"""
        print("column: ", node["name"])

    def generate_table(self, node):
        """生成table"""
        print("table: ", node["name"])

    def generate_row(self, node):
        """生成row"""
        print("row: ", node["name"])

    def generate_notification(self, node):
        """生成notification"""
        print("notification: ", node["name"])

    def is_array_of_scalar(self, kids):
        """判断子节点是否全为scalar"""
        if len(kids) == 0:
            return False
        for kid in kids:
            if self.node_dict[kid[3]]["type"] != "scalar":
                return False
        return True

    def generate_extern(self):
        """声明"""
        self.out_file_h = open(self.out_fname_h, "w", encoding="utf-8")
        f_h = self.out_file_h

        f_h.write(f"#ifndef {self.fname.upper()}_H\r\n")
        f_h.write(f"#define {self.fname.upper()}_H\r\n")
        f_h.write("\r\n")
        for extern in self.node_extern:
            f_h.write(extern)
        f_h.write("\r\n")
        for extern in self.func_extern:
            f_h.write(extern)
        f_h.write("\r\n")
        f_h.write(f"#endif /* {self.fname.upper()}_H */\r\n")
        f_h.write("\r\n")
        f_h.close()

    def process_node_dict(self, node: dict):
        """处理单个节点"""
        tp = node["type"]
        if tp == "ident":
            if self.is_array_of_scalar(node["kids"]):
                self.generate_scalar_array(node)
                return
            elif len(node["kids"]) == 0:
                self.generate_empty_tree(node)
                return
            else:
                self.generate_tree(node)
                for kid in node["kids"]:
                    self.process_node_dict(self.node_dict[kid[3]])
        elif tp == "scalar":
            self.generate_scalar(node)
            return
        elif tp == "table":
            self.generate_table(node)
            return
        elif tp == "row":
            self.generate_row(node)
            return
        elif tp == "column":
            self.generate_column(node)
            return
        elif tp == "notification":
            self.generate_notification(node)
            return

    def process(self):
        """process each mib node in the list
        starting from lowest leaves and working
        backwards to the root node - 'private'
        """
        self.process_node_dict(self.node_dict[(1, 3, 6, 4, 1)])
        f = self.out_file_c
        f.write(
            f"static const u32_t smartgen_oid_arr[] = {'{'} 1, 3, 6, 1, 4, 1, 12345 {'}'};\r\n"
        )
        f.write(
            "const struct snmp_mib smartgen_mib = SNMP_MIB_CREATE(smartgen_oid_arr, &smartgen_root.node);\r\n"
        )
        self.generate_extern()
        f.close()
        # for node in self.node_list:
        #     pprint.pprint(node)
