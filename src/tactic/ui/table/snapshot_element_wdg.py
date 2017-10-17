###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all___ = ['SnapshotLockedElementWdg', 'SnapshotFileElementWdg', 'SnapshotVersionElementWdg', 'SnapshotMetadataElementWdg','SnapshotServerEementWdg']

from tactic.ui.common import BaseTableElementWdg, BaseRefreshWdg

from pyasm.common import Config
from pyasm.biz import Snapshot
from pyasm.web import DivWdg, SpanWdg, HtmlElement, Table
from pyasm.widget import IconWdg
from pyasm.search import SearchException

import os

class SnapshotLockedElementWdg(BaseTableElementWdg):
    '''simple widget which display a task value in an element'''


    ARGS_KEYS = {
    }


    def get_key(my, snapshot):
        parent_type = snapshot.get_value("search_type")
        parent_id = snapshot.get_value("search_id")
        context = snapshot.get_value("context")
        key = "%s|%s|%s" % (parent_type, parent_id, context)
        return key




    def preprocess(my):
        my.is_locked_dict = {}
        for snapshot in my.sobjects:
            key = my.get_key(snapshot)

            is_locked = my.is_locked_dict.get(key)
            if is_locked == None:
                context = snapshot.get_value("context")
                try:
                    parent = snapshot.get_parent()
                    is_locked = Snapshot.is_locked(parent, context)

                    my.is_locked_dict[key] = is_locked
                except SearchException, e:
                    continue



    def handle_td(my, td):

        snapshot = my.get_current_sobject()
        key = my.get_key(snapshot)
        if my.is_locked_dict.get(key):
            td.add_style("background-color", "black")


    def get_display(my):
        snapshot = my.get_current_sobject()
        key = my.get_key(snapshot)
        is_locked = my.is_locked_dict.get(key)

        div = DivWdg()
        div.add_style("padding: 3px")

        if is_locked:
            icon = IconWdg("Locked by ''", IconWdg.LOCK)
            div.add(icon)
            div.add_style("text-align: center")
        else:
            div.add("&nbsp;")

        return div


class SnapshotFileElementWdg(BaseTableElementWdg):
    '''simple widget to display the main file of a snapshot'''
    def get_display(my):

        sobject = my.get_current_sobject()
        if sobject.is_insert():
            return ""

        if sobject:
            path = sobject.get_web_path_by_type()
            filename = os.path.basename(path)

            if sobject.get_value("snapshot_type") == "sequence":
                file_range = sobject.get_file_range()
                filename = "%s (%s)" % (filename, file_range.get_display() )


            widget = DivWdg()
            widget.add_style("display: inline-block")
            link = HtmlElement.href(filename, ref=path)
            link.add_attr("download", filename)
            # do this in javascript because the link doesn't
            # work for some reason
            widget.add_behavior( {
                'type': 'click',
                'filename': filename,
                'href': path,
                'cbjs_action': '''
                var a = document.createElement('a');
                a.href = bvr.href;
                a.download = bvr.filename;
                a.click();
                '''
            } )
            widget.add(link)
        else:
            widget = ""

        return widget



class SnapshotVersionElementWdg(BaseTableElementWdg):

    def get_display(my):

        top = my.top

        sobject = my.get_current_sobject()

        version = sobject.get_value(my.get_name())
        if version == '':
            top.add("No version")

        elif version == -1:
            top.add("Latest")

        elif version == 0:
            top.add("Current")

        else:

            padding = Config.get_value("checkin", "version_padding")
            if not padding:
                padding = 3

            expr = "%s%%0.%sd" % (my.get_name()[0], padding)
            value = expr % version
            top.add(value)


        return top




class SnapshotMetadataElementWdg(BaseTableElementWdg):

    def get_display(my):

        sobject = my.get_current_sobject()

        top = my.top
        from tactic.ui.checkin import SnapshotMetadataWdg
        metadata_wdg = SnapshotMetadataWdg(snapshot=sobject)
        top.add(metadata_wdg)

        return top


class SnapshotServerElementWdg(BaseTableElementWdg):
    pass


