import pprint


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

        self.out_fname = fname.split(".")[0] + ".c"
        self.out_file = open(self.out_fname, "w", encoding="utf-8")
        self.out_file.write('#include "private_mib.h"\r\n')
        self.generate_empty_line(self.out_file, 2)

    def get_datatype(self, oid):
        dt = self.node_dict[oid]["syntax"].lower()
        if dt in self.syntax_dict.keys():
            return self.syntax_dict[dt]
        return "SNMP_ASN1_TYPE_INTEGER"

    def get_access(self, oid):
        ac = self.node_dict[oid]["access"].lower()
        if ac in self.access_dict.keys():
            return self.access_dict[ac]
        return "SNMP_NODE_INSTANCE_NOT_ACCESSIBLE"

    def generate_empty_line(self, f, num):
        for _ in range(num):
            f.write("\r\n")

    def generate_set_fucntion(self, f, node):
        pass

    def generate_get_fucntion(self, f, node):
        pass

    def generate_test_fucntion(self, f, node):
        pass

    def generate_scalar_array(self, f, node):
        """生成array scalar"""
        f.write(
            f"static const struct snmp_scalar_array_node_def {node['name']}_nodes[] = {'{'}\r\n"
        )
        for kid in node["kids"]:
            f.write(
                f"    {'{'}{kid[2]}, {self.get_datatype(kid[3])}, {self.get_access(kid[3]) }{'}'}, // {kid[0]}\r\n"
            )
        f.write("};\r\n\r\n")
        f.write(f"const struct snmp_scalar_array_node {node['name']}_root =\r\n")
        f.write(
            f"    SNMP_SCALAR_CREATE_ARRAY_NODE({node['subId']}, {node['name']}_nodes,\r\n"
        )
        f.write(f"                                  {node['name']}_get_value,\r\n")
        f.write(f"                                  {node['name']}_set_test,\r\n")
        f.write(f"                                  {node['name']}_set_value);\r\n")
        print("scalar array: ", node["name"])

    def generate_empty_tree(self, f, node):
        """生成empty tree"""
        print("empty tree: ", node["name"])

    def generate_tree(self, f, node):
        """生成tree"""
        print("tree: ", node["name"])

    def generate_scalar(self, f, node):
        """生成scalar"""
        print("scalar: ", node["name"])

    def generate_column(self, f, node):
        """生成column"""
        print("column: ", node["name"])

    def generate_table(self, f, node):
        """生成table"""
        print("table: ", node["name"])

    def generate_row(self, f, node):
        """生成row"""
        print("row: ", node["name"])

    def generate_notification(self, f, node):
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

    def process_node_dict(self, node: dict):
        """处理单个节点"""
        tp = node["type"]
        if tp == "ident":
            if self.is_array_of_scalar(node["kids"]):
                self.generate_scalar_array(self.out_file, node)
                return
            elif len(node["kids"]) == 0:
                self.generate_empty_tree(self.out_file, node)
                return
            else:
                self.generate_tree(self.out_file, node)
                for kid in node["kids"]:
                    self.process_node_dict(self.node_dict[kid[3]])
        elif tp == "scalar":
            self.generate_scalar(self.out_file, node)
            return
        elif tp == "column":
            self.generate_column(self.out_file, node)
            return
        elif tp == "table":
            self.generate_table(self.out_file, node)
            return
        elif tp == "row":
            self.generate_row(self.out_file, node)
            return
        elif tp == "notification":
            self.generate_notification(self.out_file, node)
            return

    def process(self):
        """process each mib node in the list
        starting from lowest leaves and working
        backwards to the root node - 'private'
        """
        self.process_node_dict(self.node_dict[(1, 3, 6, 4, 1)])
        self.out_file.close()
        print(self.syntax_dict)
        # for node in self.node_list:
        #     pprint.pprint(node)
