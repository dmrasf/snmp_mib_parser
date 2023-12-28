import os


class MibGenerator:
    """生成C程序"""

    def __init__(self, nodelist, nodedict, nameoid, fname):
        self.node_list = nodelist
        self.node_dict = nodedict
        self.name_oid = nameoid
        self.syntax_dict = {
            "integer": "SNMP_ASN1_TYPE_INTEGER",
            "integer32": "SNMP_ASN1_TYPE_INTEGER",
            "unsigned32": "SNMP_ASN1_TYPE_UNSIGNED32",
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
        self.syntax_ctype_dict = {
            "integer": "s32_t",
            "integer32": "s32_t",
            "unsigned32": "u32_t",
            "octet": "const char*",
            "displaystring": "const char*",
            "object": "u32_t",
            "timeticks": "u32_t",
            "gauge": "u32_t",
            "gauge32": "u32_t",
            "counter": "u32_t",
            "counter32": "u32_t",
            "ipaddress": "const char*",
            "physaddress": "const char*",
            "networkaddress": "const char*",
        }
        self.datatype_dict = {
            "integer": "SNMP_VARIANT_VALUE_TYPE_S32",
            "integer32": "SNMP_VARIANT_VALUE_TYPE_S32",
            "unsigned32": "SNMP_VARIANT_VALUE_TYPE_U32",
            "octet": "SNMP_VARIANT_VALUE_TYPE_CONST_PTR",
            "displaystring": "SNMP_VARIANT_VALUE_TYPE_CONST_PTR",
            "object": "SNMP_VARIANT_VALUE_TYPE_U32",
            "timeticks": "SNMP_VARIANT_VALUE_TYPE_U32",
            "gauge": "SNMP_VARIANT_VALUE_TYPE_U32",
            "gauge32": "SNMP_VARIANT_VALUE_TYPE_U32",
            "counter": "SNMP_VARIANT_VALUE_TYPE_U32",
            "counter32": "SNMP_VARIANT_VALUE_TYPE_U32",
            "ipaddress": "SNMP_VARIANT_VALUE_TYPE_U32",
            "physaddress": "SNMP_VARIANT_VALUE_TYPE_U32",
            "networkaddress": "SNMP_VARIANT_VALUE_TYPE_U32",
        }
        self.access_dict = {
            "read-only": "SNMP_NODE_INSTANCE_READ_ONLY",
            "read-write": "SNMP_NODE_INSTANCE_READ_WRITE",
            "write-only": "SNMP_NODE_INSTANCE_WRITE_ONLY",
            "not-access": "SNMP_NODE_INSTANCE_NOT_ACCESSIBLE",
        }

        (_, fname) = os.path.split(fname)

        self.fname = fname.split(".")[0].replace("-", "_")
        self.out_fname_c = self.fname + ".c"
        self.out_fname_h = self.fname + ".h"
        self.out_file_c = open(self.out_fname_c, "w", encoding="utf-8")
        self.out_file_h = open(self.out_fname_h, "w", encoding="utf-8")
        self.node_extern = []
        self.func_extern = []
        self.struct_declare = []
        self.out_file_c.write(f'#include "{self.out_fname_h}"\n\n')

    def get_syntax_type(self, syntax):
        """获取syntax类型"""
        dt = syntax.lower()
        if dt in self.syntax_dict:
            return self.syntax_dict[dt]
        return "SNMP_ASN1_TYPE_INTEGER"

    def get_ctype(self, syntax):
        """获取c类型"""
        dt = syntax.lower()
        if dt in self.syntax_ctype_dict:
            return self.syntax_ctype_dict[dt]
        return "u32_t"

    def get_data_type(self, syntax):
        """获取datatype table"""
        dt = syntax.lower()
        if dt in self.datatype_dict:
            return self.datatype_dict[dt]
        return "SNMP_VARIANT_VALUE_TYPE_U32"

    def get_access(self, access):
        """获取权限"""
        ac = access.lower()
        if ac in self.access_dict:
            return self.access_dict[ac]
        return "SNMP_NODE_INSTANCE_NOT_ACCESSIBLE"

    def generate_scalar_array_get_method(self, node):
        """生成scalar_array_get_method"""
        f = self.out_file_c
        self.func_extern.append(
            f"s16_t {node['name']}_get_value(const struct snmp_scalar_array_node_def *scalar, "
            "void *value);\n"
        )
        f.write(
            f"s16_t {node['name']}_get_value(const struct snmp_scalar_array_node_def *scalar, "
            "void *value)\n"
        )
        f.write("{\n")
        f.write("    u32_t *uint_ptr = (u32_t *)value;\n")
        f.write("    switch (scalar->oid) {\n")
        for kid in node["kids"]:
            f.write(f"    case {kid[2]}: // {kid[0]}\n")
            f.write(f"       *uint_ptr = {kid[2]};\n")
            f.write("        break;\n")
        f.write("    default:\n")
        f.write("        break;\n")
        f.write("    }\n")
        f.write("    return sizeof(*uint_ptr);\n")
        f.write("}\n")
        f.write("\n")

    def generate_scalar_array_test_method(self, node):
        """生成scalar_array_test_method"""
        f = self.out_file_c
        self.func_extern.append(
            f"snmp_err_t {node['name']}_set_test(const struct snmp_scalar_array_node_def *scalar, "
            "u16_t len, void *value);\n"
        )
        f.write(
            f"snmp_err_t {node['name']}_set_test(const struct snmp_scalar_array_node_def *scalar, "
            "u16_t len, void *value)\n"
        )
        f.write("{\n")
        f.write("    snmp_err_t ret = SNMP_ERR_NOERROR;\n")
        f.write("    return ret;\n")
        f.write("}\n")
        f.write("\n")

    def generate_scalar_array_set_method(self, node):
        """生成scalar_array_set_method"""
        f = self.out_file_c
        self.func_extern.append(
            f"snmp_err_t {node['name']}_set_value(const struct snmp_scalar_array_node_def *scalar, "
            "u16_t len, void *value);\n"
        )
        f.write(
            f"snmp_err_t {node['name']}_set_value(const struct snmp_scalar_array_node_def *scalar, "
            "u16_t len, void *value)\n"
        )
        f.write("{\n")
        f.write("    snmp_err_t ret = SNMP_ERR_NOERROR;\n")
        f.write("    return ret;\n")
        f.write("}\n")
        f.write("\n")

    def generate_table_get_cell_value_method(self, node):
        """生成table_get_cell_value_method"""
        f = self.out_file_c
        self.func_extern.append(
            f"snmp_err_t {node['parent_name']}_get_cell_value(const u32_t *column, "
            "const u32_t *row_oid, u8_t row_oid_len, union snmp_variant_value *value, "
            "u32_t *value_len);\n"
        )
        f.write(
            f"snmp_err_t {node['parent_name']}_get_cell_value(const u32_t *column, "
            "const u32_t *row_oid, u8_t row_oid_len, union snmp_variant_value *value, "
            "u32_t *value_len)\n"
        )
        f.write("{\n")
        f.write("    u32_t index = 0;\n\n")
        f.write("    if (row_oid_len != 1)\n")
        f.write("        return SNMP_ERR_NOACCESS;\n\n")
        f.write("    index = row_oid[0];\n")
        f.write("    if (index > 5)\n")
        f.write("        return SNMP_ERR_NOACCESS;\n\n")
        f.write("    switch (*column) {\n")
        for kid in node["kids"]:
            f.write(f"    case {kid[2]}: // {kid[0]}\n")
            f.write("        value->u32 = *column;\n")
            f.write("        *value_len = sizeof(value->u32);\n")
            f.write("        break;\n")
        f.write("    default:\n")
        f.write("        break;\n")
        f.write("    }\n\n")
        f.write("    return SNMP_ERR_NOERROR;\n")
        f.write("}\n\n")

    def generate_table_get_next_cell_instance_and_value_method(self, node):
        """生成table_get_next_cell_instance_and_value_method"""
        f = self.out_file_c
        self.func_extern.append(
            f"snmp_err_t {node['parent_name']}_get_next_cell_instance_and_value("
            "const u32_t *column, struct snmp_obj_id *row_oid, "
            "union snmp_variant_value *value, u32_t *value_len);\n"
        )
        f.write(
            f"snmp_err_t {node['parent_name']}_get_next_cell_instance_and_value("
            "const u32_t *column, struct snmp_obj_id *row_oid, "
            "union snmp_variant_value *value, u32_t *value_len)\n"
        )
        f.write("{\n")
        f.write("    u32_t index = 1;\n\n")
        f.write("    u32_t oid_arr[] = {index};\n")
        f.write(
            "    snmp_oid_assign(row_oid, oid_arr, sizeof(oid_arr) / sizeof(oid_arr[0]));\n\n"
        )
        f.write("    switch (*column) {\n")
        for kid in node["kids"]:
            f.write(f"    case {kid[2]}: // {kid[0]}\n")
            f.write("        value->u32 = *column;\n")
            f.write("        *value_len = sizeof(value->u32);\n")
            f.write("        break;\n")
        f.write("    default:\n")
        f.write("        break;\n")
        f.write("    }\n\n")
        f.write("    return SNMP_ERR_NOERROR;\n")
        f.write("}\n\n")

    def generate_scalar_get_method(self, node):
        """生成scalar_get_method"""
        f = self.out_file_c
        self.func_extern.append(
            f"s16_t {node['parent_name']}_{node['name']}_get_value("
            "struct snmp_node_instance *node, void *value);\n"
        )
        f.write(
            f"s16_t {node['parent_name']}_{node['name']}_get_value("
            "struct snmp_node_instance *node, void *value)\n"
        )
        f.write("{\n")
        f.write("    u32_t *uint_ptr = (u32_t *)value;\n\n")
        f.write(f"    *uint_ptr = {node['subId']};\n")
        f.write("    return sizeof(*uint_ptr);\n")
        f.write("}\n\n")

    def generate_scalar_test_method(self, node):
        """生成scalar_test_method"""
        f = self.out_file_c
        self.func_extern.append(
            f"snmp_err_t {node['parent_name']}_{node['name']}_set_test("
            "struct snmp_node_instance *node, u16_t len, void *value);\n"
        )
        f.write(
            f"snmp_err_t {node['parent_name']}_{node['name']}_set_test("
            "struct snmp_node_instance *node, u16_t len, void *value)\n"
        )
        f.write("{\n")
        f.write("    snmp_err_t ret = SNMP_ERR_NOERROR;\n\n")
        f.write("    return ret;\n")
        f.write("}\n\n")

    def generate_scalar_set_method(self, node):
        """生成scalar_set_method"""
        f = self.out_file_c
        self.func_extern.append(
            f"snmp_err_t {node['parent_name']}_{node['name']}_set_value("
            "struct snmp_node_instance *node, u16_t len, void *value);\n"
        )
        f.write(
            f"snmp_err_t {node['parent_name']}_{node['name']}_set_value("
            "struct snmp_node_instance *node, u16_t len, void *value)\n"
        )
        f.write("{\n")
        f.write("    snmp_err_t ret = SNMP_ERR_NOERROR;\n\n")
        f.write("    return ret;\n")
        f.write("}\n\n")

    def generate_scalar_array(self, node):
        """生成array scalar"""
        print("scalar array: ", node["name"])
        f = self.out_file_c
        self.node_extern.append(
            f"extern const struct snmp_scalar_array_node {node['name']}_root;\n"
        )

        self.generate_scalar_array_get_method(node)
        self.generate_scalar_array_test_method(node)
        self.generate_scalar_array_set_method(node)
        f.write(
            f"static const struct snmp_scalar_array_node_def {node['name']}_nodes[] = {'{'}\n"
        )
        for kid in node["kids"]:
            f.write(
                f"    {'{'}{kid[2]}, {self.get_syntax_type(self.node_dict[kid[3]]['syntax'])}, "
                f"{self.get_access(self.node_dict[kid[3]]['access']) }{'}'}, // {kid[0]}\n"
            )
        f.write("};\n")
        f.write(f"const struct snmp_scalar_array_node {node['name']}_root =\n")
        f.write(
            f"    SNMP_SCALAR_CREATE_ARRAY_NODE({node['subId']}, {node['name']}_nodes,\n"
        )
        f.write(f"                                  {node['name']}_get_value,\n")
        f.write(f"                                  {node['name']}_set_test,\n")
        f.write(f"                                  {node['name']}_set_value);\n\n")

    def generate_empty_tree(self, node):
        """生成empty tree"""
        print("empty tree: ", node["name"])
        f = self.out_file_c
        self.node_extern.append(
            f"extern const struct snmp_tree_node {node['name']}_root;\n"
        )
        f.write(
            f"static const struct snmp_node *const {node['name']}_nodes[] = {'{'}NULL{'}'};\n"
        )
        f.write(
            f"const struct snmp_tree_node {node['name']}_root = "
            f"SNMP_CREATE_EMPTY_TREE_NODE({node['subId']});\n\n"
        )

    def generate_tree(self, node):
        """生成tree"""
        print("tree: ", node["name"])
        f = self.out_file_c
        self.node_extern.append(
            f"extern const struct snmp_tree_node {node['name']}_root;\n"
        )
        f.write(
            f"static const struct snmp_node *const {node['name']}_nodes[] = {'{'}\n"
        )
        for kid in node["kids"]:
            if (
                self.is_array_of_scalar(self.node_dict[kid[3]]["kids"])
                or kid[1] == "scalar"
                or kid[1] == "table"
            ):
                f.write(f"    &{kid[0]}_root.node.node, // {kid[0]}\n")
            elif kid[1] != "notification":
                f.write(f"    &{kid[0]}_root.node, // {kid[0]}\n")
            else:
                f.write(f"    NULL, // {kid[0]}\n")
        f.write("};\n")
        f.write(
            f"const struct snmp_tree_node {node['name']}_root = "
            f"SNMP_CREATE_TREE_NODE({node['subId']}, {node['name']}_nodes);\n\n"
        )

    def generate_scalar(self, node):
        """生成scalar"""
        print("scalar: ", node["name"])
        f = self.out_file_c
        self.node_extern.append(
            f"extern const struct snmp_scalar_node {node['name']}_root;\n"
        )
        self.generate_scalar_get_method(node)
        set_func_name = "NULL, NULL"
        if node["access"] != "read-only" and node["access"] != "not-access":
            self.generate_scalar_test_method(node)
            self.generate_scalar_set_method(node)
            set_func_name = (
                f"{node['parent_name']}_{node['name']}_set_test, "
                + f"{node['parent_name']}_{node['name']}_set_value"
            )
        f.write(
            f"const struct snmp_scalar_node {node['name']}_root = "
            f"SNMP_SCALAR_CREATE_NODE({node['subId']}, "
            f"{self.get_access(node['access'])}, {self.get_syntax_type(node['syntax'])}, "
            f"{node['parent_name']}_{node['name']}_get_value, {set_func_name});\n\n"
        )

    def generate_table(self, node):
        """生成table"""
        print("table: ", node["name"])
        row_name = ""
        if len(node["kids"]) == 1:
            self.generate_row(self.node_dict[node["kids"][0][3]])
            row_name = node["kids"][0][0]
            row_name = row_name + "_"
        f = self.out_file_c
        self.node_extern.append(
            f"extern const struct snmp_table_simple_node {node['name']}_root;\n"
        )
        f.write(f"const struct snmp_table_simple_node {node['name']}_root =\n")
        f.write(
            f"    SNMP_TABLE_CREATE_SIMPLE({node['subId']}, {node['name']}_{row_name}row,\n"
        )
        f.write(f"                             {node['name']}_get_cell_value,\n")
        f.write(
            f"                             {node['name']}_get_next_cell_instance_and_value);\n"
        )
        f.write("\n")

    def generate_row(self, node):
        """生成row"""
        print("row: ", node["name"])
        self.generate_table_get_cell_value_method(node)
        self.generate_table_get_next_cell_instance_and_value_method(node)
        f = self.out_file_c
        f.write(
            "static const struct snmp_table_simple_col_def "
            f"{node['parent_name']}_{node['name']}_row[] = {'{'}\n"
        )
        for kid in node["kids"]:
            f.write(
                f"    {'{'}{kid[2]}, {self.get_syntax_type(self.node_dict[kid[3]]['syntax'])}, "
                f"{self.get_data_type(self.node_dict[kid[3]]['syntax'])}{'}'}, // {kid[0]}\n"
            )
        f.write("};\n")

    def generate_column(self, node):
        """生成column"""
        print("column: ", node["name"])

    def generate_notification(self, node):
        """生成notification"""
        print("notification: ", node["name"])
        if len(node["objects"]) == 0:
            return
        self.struct_declare.append(f"struct {node['name']} {'{'}\n")
        for obj in node["objects"]:
            kid = self.node_dict[self.name_oid[obj]]
            self.struct_declare.append(
                f"    {self.get_ctype(kid['syntax'])} {kid['name']};\n"
            )
        self.struct_declare.append("};\n\n")
        self.func_extern.append(
            f"err_t send_trap_{node['name']}(const struct {node['name']} *trap);\n"
        )
        f = self.out_file_c
        f.write(f"err_t send_trap_{node['name']}(const struct {node['name']} *trap)\n")
        f.write("{\n")
        f.write("    err_t ret = ERR_OK;\n")
        f.write(
            "    const struct snmp_obj_id trap_oid = "
            f"{'{'}{len(node['parent'])+1}, {'{'}{node['parent']}, "
            f"{node['subId']}{'}'}{'}'};\n\n".translate({ord(c): None for c in "()"})
        )
        for obj in node["objects"]:
            kid = self.node_dict[self.name_oid[obj]]
            f.write(
                f"    const struct snmp_obj_id oid_{obj} = "
                f"{'{'}{len(kid['parent'])+1}, {'{'}{kid['parent']}, "
                f"{kid['subId']}{'}'}{'}'};\n".translate({ord(c): None for c in "()"})
            )
        f.write("\n")
        for obj in node["objects"]:
            kid = self.node_dict[self.name_oid[obj]]
            f.write(
                f"    struct snmp_varbind *vb_{kid['name']} = "
                "(struct snmp_varbind*)calloc(1, sizeof(struct snmp_varbind));\n"
            )
        f.write("\n")
        for i, obj in enumerate(node["objects"]):
            kid = self.node_dict[self.name_oid[obj]]
            f.write(
                f"    snmp_oid_assign(&vb_{kid['name']}->oid, "
                f"oid_{kid['name']}.id, oid_{kid['name']}.len);\n"
            )
            f.write(
                f"    vb_{kid['name']}->type = {self.get_syntax_type(kid['syntax'])};\n"
            )
            if (
                kid["syntax"].lower() == "octet"
                or kid["syntax"].lower() == "displaystring"
            ):
                f.write(f"    vb_{kid['name']}->value = (void *)trap->{kid['name']};\n")
                f.write(
                    f"    vb_{kid['name']}->value_len = strlen(trap->{kid['name']});\n"
                )
            else:
                f.write(
                    f"    vb_{kid['name']}->value = (void *)&trap->{kid['name']};\n"
                )
                f.write(
                    f"    vb_{kid['name']}->value_len = sizeof(trap->{kid['name']});\n"
                )
            if i + 1 < len(node["objects"]):
                kid_next = self.node_dict[self.name_oid[node["objects"][i + 1]]]
                f.write(f"    vb_{kid['name']}->next = vb_{kid_next['name']};\n")
            if i > 0:
                kid_prev = self.node_dict[self.name_oid[node["objects"][i - 1]]]
                f.write(f"    vb_{kid['name']}->prev = vb_{kid_prev['name']};\n")
            f.write("\n")
        first_kid = self.node_dict[self.name_oid[node["objects"][0]]]
        f.write(
            "    ret = snmp_send_trap(&trap_oid, SNMP_GENTRAP_ENTERPRISE_SPECIFIC, "
            f"1, vb_{first_kid['name']});\n\n"
        )
        for obj in node["objects"]:
            kid = self.node_dict[self.name_oid[obj]]
            f.write(f"    free(vb_{kid['name']});\n")
        f.write("    return ret;\n")
        f.write("}\n\n")

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
        f_h = self.out_file_h
        f_h.write(f"#ifndef {self.fname.upper()}_H\n")
        f_h.write(f"#define {self.fname.upper()}_H\n\n")
        f_h.write('#include "snmp_task.h"\n\n')
        for struct in self.struct_declare:
            f_h.write(struct)
        for extern in self.node_extern:
            f_h.write(extern)
        f_h.write("\n")
        for extern in self.func_extern:
            f_h.write(extern)
        f_h.write("\n")
        f_h.write(f"#endif /* {self.fname.upper()}_H */\n")
        f_h.write("\n")
        f_h.close()

    def generate_mibs(self, node):
        """mibs"""
        f = self.out_file_c
        for kid in node["kids"]:
            f.write(
                f"static const u32_t {kid[0]}_oid_arr[] = {'{'} 1, 3, 6, 1, 4, 1, {kid[2]} {'}'};\n"
            )
            f.write(
                f"const struct snmp_mib {kid[0]}_mib = "
                f"SNMP_MIB_CREATE({kid[0]}_oid_arr, &{kid[0]}_root.node);\n"
            )
            self.node_extern.append(f"extern const struct snmp_mib {kid[0]}_mib;\n")

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
        elif tp == "notification":
            self.generate_notification(node)
            return

    def process(self):
        """process each mib node in the list
        starting from lowest leaves and working
        backwards to the root node - 'private'
        """
        self.process_node_dict(self.node_dict[(1, 3, 6, 4, 1)])
        self.generate_mibs(self.node_dict[(1, 3, 6, 4, 1)])
        self.generate_extern()
        f = self.out_file_c
        f.close()
        # for node in self.node_list:
        #     pprint.pprint(node)
