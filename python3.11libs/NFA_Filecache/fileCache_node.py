import hou
from HDABuilder import HDABuilder

class FileCacheNode(HDABuilder.HDABuilder):
    """

Build in the Houdini Python Console:


from importlib import reload

from NFA_Filecache import fileCache_node
from HDABuilder import HDABuilder

reload(fileCache_node)
reload(HDABuilder)

fileCache_node.FileCacheNode(
    name="nfa_filecache",
    hda_file_name="C:/pipeline/houdini/hsite/houdini21.0/otls/nfa_filecache.hdanc",
    description="nfa_filecache",
    min_num_inputs=1,
    max_num_inputs=1,
    version="1.0",
    hda_type=HDABuilder.HDATypes.SOPNET,
    icon="opdef:/Sop/nfa_filecache?IconSVG"
    )

    """
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            builded_nodes=self.build_hda_nodes,
            parameter_interface=self.build_hda_parms,
            **kwargs
            )
        self.build()

    def build_hda_parms(self):
        hou_parm_template_group = hou.ParmTemplateGroup()

        time_dependent = hou.ToggleParmTemplate(
            "time_dependent",
            "Time Dependent",
            default_value=True,
            script_callback_language=hou.scriptLanguage.Python
            )

        load_from_disk = hou.ToggleParmTemplate(
            "load_from_disk",
            "Load From Disk",
            default_value=False,
            script_callback_language=hou.scriptLanguage.Python
            )

        start_end_inc = hou.FloatParmTemplate(
            "start_end_inc",
            "Start/End/Inc",
            3,
            default_value=([0, 0, 1]),
            default_expression=(["$FSTART", "$FEND", ""]),
            default_expression_language=([hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript]),
            min=-1,
            max=1,
            min_is_strict=False,
            max_is_strict=False,
            look=hou.parmLook.Regular,
            naming_scheme=hou.parmNamingScheme.XYZW,
            join_with_next=True,
            script_callback_language=hou.scriptLanguage.Python
            )
        start_end_inc.setConditional(hou.parmCondType.DisableWhen, "{ time_dependent == 0 }")

        filetype = hou.MenuParmTemplate(
            "filetype",
            "File Type",
            menu_items=([".bgeo.sc", ".vdb"]),
            menu_labels=(["bgeo.sc", "vdb"]),
            default_value=0,
            icon_names=([]),
            item_generator_script="",
            item_generator_script_language=hou.scriptLanguage.Python,
            menu_type=hou.menuType.Normal,
            menu_use_token=False,
            is_button_strip=False,
            strip_uses_icons=False,
            is_label_hidden=True,
            script_callback_language=hou.scriptLanguage.Python
            )

        filetype.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})

        sepparm = hou.SeparatorParmTemplate("sepparm")
        sepparm.setTags({"sidefx::layout_height": "small", "sidefx::look": "blank"})

        task = hou.StringParmTemplate(
            "task",
            "Task",
            1,
            default_value=([""]),
            naming_scheme=hou.parmNamingScheme.Base1,
            string_type=hou.stringParmType.Regular,
            menu_items=([]),
            menu_labels=([]),
            icon_names=([]),
            item_generator_script="",
            item_generator_script_language=hou.scriptLanguage.Python,
            menu_type=hou.menuType.Normal,
            script_callback_language=hou.scriptLanguage.Python
            )

        folder2 = hou.FolderParmTemplate(
            "folder2",
            "Folder Name",
            folder_type=hou.folderType.Simple,
            default_value=0,
            ends_tab_group=False
            )
        folder2.setTags({"group_type": "simple"})

        sepparm2 = hou.SeparatorParmTemplate("sepparm2")
        sepparm2.setTags({"sidefx::layout_height": "small", "sidefx::look": "blank"})

        is_sim = hou.ToggleParmTemplate(
            "is_sim",
            "Cache is Sim",
            default_value=False,
            script_callback_language=hou.scriptLanguage.Python
            )

        save_to_disk = hou.ButtonParmTemplate(
            "save_to_disk",
            "Save to Disk",
            join_with_next=True,
            script_callback="from NFA_Filecache import fileCache; fileCache.start(hou.pwd())",
            script_callback_language=hou.scriptLanguage.Python
            )

        save_to_disk_bg = hou.ButtonParmTemplate(
            "save_to_disk_bg",
            "Save to Disk in Background",
            join_with_next=True,
            script_callback_language=hou.scriptLanguage.Python
            )

        save_to_disk_farm = hou.ButtonParmTemplate(
            "save_to_disk_farm",
            "Save to Disk over Farm",
            script_callback="from NFA_Filecache import fileCache; fileCache.start_farm(hou.pwd())",
            script_callback_language=hou.scriptLanguage.Python
            )

        folder0 = hou.FolderParmTemplate(
            "folder0",
            "Clean Geo",
            folder_type=hou.folderType.Tabs,
            default_value=0,
            ends_tab_group=True
            )

        clean_att = hou.ToggleParmTemplate(
            "clean_att",
            "Clean Attributes",
            default_value=False,
            script_callback_language=hou.scriptLanguage.Python
            )

        keep_custom = hou.ToggleParmTemplate(
            "keep_custom",
            "Keep Custom Attributes",
            default_value=False,
            script_callback_language=hou.scriptLanguage.Python
            )
        keep_custom.setConditional(hou.parmCondType.DisableWhen, "{ clean_att == 0 }")

        sepparm3 = hou.SeparatorParmTemplate("sepparm3")
        sepparm3.setTags({"sidefx::layout_height": "small", "sidefx::look": "blank"})

        clean_grp = hou.ToggleParmTemplate(
            "clean_grp",
            "Clean Groups",
            default_value=False,
            script_callback_language=hou.scriptLanguage.Python
            )

        keep_custom_grp = hou.ToggleParmTemplate(
            "keep_custom_grp",
            "Keep Custom Groups",
            default_value=False,
            script_callback_language=hou.scriptLanguage.Python
            )
        keep_custom_grp.setConditional(hou.parmCondType.DisableWhen, "{ clean_grp == 0 }")

        folder1 = hou.FolderParmTemplate(
            "folder1",
            "Keep Custom",
            folder_type=hou.folderType.Simple,
            default_value=0,
            ends_tab_group=False
            )
        folder1.setConditional(hou.parmCondType.DisableWhen, "{ keep_custom == 0 }")
        folder1.setTags({"group_type": "simple"})

        point_att = hou.ToggleParmTemplate(
            "point_att",
            "Label",
            default_value=False,
            is_label_hidden=True,
            join_with_next=True,
            script_callback_language=hou.scriptLanguage.Python
            )

        pot_att_sel2 = hou.StringParmTemplate(
            "pot_att_sel2",
            "Point Attributes",
            1,
            default_value=([""]),
            naming_scheme=hou.parmNamingScheme.Base1,
            string_type=hou.stringParmType.Regular,
            menu_items=([]),
            menu_labels=([]),
            icon_names=([]),
            item_generator_script="opmenu -l -a attribute1 pot_att_del",
            item_generator_script_language=hou.scriptLanguage.Python,
            menu_type=hou.menuType.StringToggle,
            script_callback_language=hou.scriptLanguage.Python
            )
        pot_att_sel2.setConditional(hou.parmCondType.DisableWhen, "{ point_att == 0 }")

        ver_att = hou.ToggleParmTemplate(
            "ver_att",
            "Label",
            default_value=False,
            is_label_hidden=True,
            join_with_next=True,
            script_callback_language=hou.scriptLanguage.Python
            )

        ver_att_sel = hou.StringParmTemplate(
            "ver_att_sel",
            "Vertex Attributes",
            1,
            default_value=([""]),
            naming_scheme=hou.parmNamingScheme.Base1,
            string_type=hou.stringParmType.Regular,
            menu_items=([]),
            menu_labels=([]),
            icon_names=([]),
            item_generator_script="opmenu -l -a attribute1 pot_att_del",
            item_generator_script_language=hou.scriptLanguage.Python,
            menu_type=hou.menuType.StringToggle,
            script_callback_language=hou.scriptLanguage.Python
            )
        ver_att_sel.setConditional(hou.parmCondType.DisableWhen, "{ ver_att == 0 }")

        prim_att = hou.ToggleParmTemplate(
            "prim_att",
            "Label",
            default_value=False,
            is_label_hidden=True,
            join_with_next=True,
            script_callback_language=hou.scriptLanguage.Python
            )

        prim_att_sel = hou.StringParmTemplate(
            "prim_att_sel",
            "Primitive Attributes",
            1,
            default_value=([""]),
            naming_scheme=hou.parmNamingScheme.Base1,
            string_type=hou.stringParmType.Regular,
            menu_items=([]),
            menu_labels=([]),
            icon_names=([]),
            item_generator_script="opmenu -l -a attribute1 pot_att_del",
            item_generator_script_language=hou.scriptLanguage.Python,
            menu_type=hou.menuType.StringToggle,
            script_callback_language=hou.scriptLanguage.Python
            )
        prim_att_sel.setConditional(hou.parmCondType.DisableWhen, "{ prim_att == 0 }")

        det_att = hou.ToggleParmTemplate(
            "det_att",
            "Label",
            default_value=False,
            is_label_hidden=True,
            join_with_next=True,
            script_callback_language=hou.scriptLanguage.Python
            )

        det_att_sel = hou.StringParmTemplate(
            "det_att_sel",
            "Detail Attributes",
            1,
            default_value=([""]),
            naming_scheme=hou.parmNamingScheme.Base1,
            string_type=hou.stringParmType.Regular,
            menu_items=([]),
            menu_labels=([]),
            icon_names=([]),
            item_generator_script="opmenu -l -a attribute1 pot_att_del",
            item_generator_script_language=hou.scriptLanguage.Python,
            menu_type=hou.menuType.StringToggle,
            script_callback_language=hou.scriptLanguage.Python
            )
        det_att_sel.setConditional(hou.parmCondType.DisableWhen, "{ det_att == 0 }")

        keep_custom_groups = hou.FolderParmTemplate(
            "keep_custom_groups",
            "Keep Custom Groups",
            folder_type=hou.folderType.Simple,
            default_value=0,
            ends_tab_group=False
            )
        keep_custom_groups.setConditional(hou.parmCondType.DisableWhen, "{ keep_custom_grp == 0 }")
        keep_custom_groups.setTags({"group_type": "simple"})

        groups_to_keep = hou.StringParmTemplate(
            "groups_to_keep",
            "Groups To Keep",
            1,
            default_value=([""]),
            naming_scheme=hou.parmNamingScheme.Base1,
            string_type=hou.stringParmType.Regular,
            menu_items=([]),
            menu_labels=([]),
            icon_names=([]),
            item_generator_script="",
            item_generator_script_language=hou.scriptLanguage.Python,
            menu_type=hou.menuType.StringToggle,
            script_callback_language=hou.scriptLanguage.Python
            )
        
        folder0_entries = (
            clean_att,
            keep_custom,
            sepparm3,
            clean_grp,
            keep_custom_grp
        )
        for i in folder0_entries:
            folder0.addParmTemplate(i)

        folder1_entries = (
            point_att,
            pot_att_sel2,
            ver_att,
            ver_att_sel,
            prim_att,
            prim_att_sel,
            det_att,
            det_att_sel
        )
        keep_custom_groups.addParmTemplate(groups_to_keep)

        for i in folder1_entries:
            folder1.addParmTemplate(i)

        node_entries = (
            time_dependent,
            load_from_disk,
            start_end_inc,
            filetype,
            sepparm,
            task,
            sepparm2,
            is_sim,
            save_to_disk,
            save_to_disk_bg,
            save_to_disk_farm,

            folder0,
            folder1,
            keep_custom_groups
            )
        

        for i in node_entries:
            hou_parm_template_group.append(i)
        
        return hou_parm_template_group



    def build_hda_nodes(self):

        expression1 = """ch("../point_att")"""
        expression2 = """ch("../ver_att")"""
        expression3 = """ch("../prim_att")"""
        expression4 = """ch("../det_att")"""
        expression5 = """ch("../keep_custom")"""
        expression6 = """ch("../clean_grp")"""
        expression7 = """ch("../clean_att")"""
        expression8 = """ch("../load_from_disk")"""
        expression9 = """ch("../time_dependent")"""

        hda_node = self.hda

        hda_input_node = hda_node.item("1")

        keep_standard = hda_node.createNode("attribdelete", "KEEP_STANDARD")
        keep_standard.setInput(0, hda_input_node)
        keep_standard.parm("ptdel").set("* ^v ^pscale ^age ^life ^id")
        keep_standard.parm("vtxdel").set("* ^N *^uv")
        keep_standard.parm("primdel").set("*")
        keep_standard.parm("dtldel").set("*")

        keep_custom = hda_node.createNode("attribdelete", "KEEP_CUSTOM")
        keep_custom.setInput(0, hda_input_node)
        keep_custom.parm("doptdel").setExpression(expression1)
        keep_custom.parm("dovtxdel").setExpression(expression2)
        keep_custom.parm("doprimdel").setExpression(expression3)
        keep_custom.parm("dodtldel").setExpression(expression4)

        attrib_copy = hda_node.createNode("attribcopy")
        attrib_copy.setInput(0, keep_standard)
        attrib_copy.setInput(1, keep_custom)
        attrib_copy.parm("attribname").set("*")

        switch_1 = hda_node.createNode("switch")
        switch_1.setInput(0, keep_standard)
        switch_1.setInput(1, attrib_copy)
        switch_1.parm("input").setExpression(expression5)

        group_delete = hda_node.createNode("groupdelete")
        group_delete.setInput(0, switch_1)
        group_delete.parm("group1").set("group1")
        group_delete.parm("removegrp").set(1)
        
        switch_2 = hda_node.createNode("switch")
        switch_2.setInput(0, switch_1)
        switch_2.setInput(1, group_delete)
        switch_2.parm("input").setExpression(expression6)

        switch_3 = hda_node.createNode("switch")
        switch_3.setInput(0, hda_input_node)
        switch_3.setInput(1, switch_2)
        switch_3.parm("input").setExpression(expression7)

        rop_geo = hda_node.createNode("rop_geometry", "ROP_GEO")
        rop_geo.setInput(0, switch_3)
        rop_geo.parm("sopoutput").set("")
        rop_geo.parm("trange").setExpression(expression9)

        file_in = hda_node.createNode("file", "FILE_IN")

        switch_if = hda_node.createNode("switchif")
        switch_if.setInput(0, switch_3)
        switch_if.setInput(1, file_in)
        switch_if.parm("expr1").setExpression(expression8)

        output = hda_node.createNode("output")
        output.setInput(0, switch_if)

        rop_net = hda_node.createNode("ropnet", "DEADLINE")

        fetch = rop_net.createNode("fetch")
        fetch.parm("source").set("../../ROP_GEO")

        dependent_deadline = rop_net.createNode("deadline", "FRAME_DEPENDENT")
        dependent_deadline.setInput(0, fetch)
        dependent_deadline.parm("dl_job_name").deleteAllKeyframes()
        dependent_deadline.parm("dl_job_name").set("")
        dependent_deadline.parm("dl_chunk_size").setExpression("$FEND-$FSTART")
        
        non_dependent_deadline = rop_net.createNode("deadline", "NON_FRAME_DEPENDENT")
        non_dependent_deadline.setInput(0, fetch)
        non_dependent_deadline.parm("dl_job_name").deleteAllKeyframes()
        non_dependent_deadline.parm("dl_job_name").set("")

        rop_net.layoutChildren()
        hda_node.layoutChildren()

