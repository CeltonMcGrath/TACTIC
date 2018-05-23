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
__all__ = ['BaseRefreshWdg']

import types

from pyasm.common import Common, Xml
from pyasm.search import Search, SObject
from pyasm.web import Widget, WebContainer, WidgetException, HtmlElement, DivWdg, WidgetSettings

class BaseRefreshWdg(Widget):
    def __init__(self, **kwargs):
        # get the them from cgi
        self.handle_args(kwargs)
        self.top = DivWdg()

        super(BaseRefreshWdg,self).__init__()

    #
    # Define a standard format for widgets
    #
    # Get it from web_form_values()
    ARGS_KEYS = {}
    def get_args_keys(cls):
        '''external settings which populate the widget'''
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)


    CATEGORY_KEYS = {}
    def get_category_keys(cls):
        return cls.CATEGORY_KEYS
    get_category_keys = classmethod(get_category_keys)




    # DEPRECATED: use ARGS_KEYS
    ARGS_OPTIONS = []
    def get_args_options(cls):
        '''external settings which populate the widget'''
        return cls.ARGS_OPTIONS
    get_args_options = classmethod(get_args_options)


    def handle_args(self, kwargs):
        # verify the args
        #args_keys = self.get_args_keys()

        if kwargs.get("include_form_values") in [True, 'true']:
            web = WebContainer.get_web()
            args_keys = self.get_args_keys()
            for key in args_keys.keys():
                if web and not kwargs.has_key(key):
                    value = web.get_form_value(key)
                    kwargs[key] = value
        else:
            args_keys = self.get_args_keys()
            for key in args_keys.keys():
                if not kwargs.has_key(key):
                    kwargs[key] = ''
        self.kwargs = kwargs


    def set_arg(self, name, value):
        self.kwargs[name] = value


    def get_top(self):
        return self.top

    def add_class(self, class_name):
        self.top.add_class(class_name)

    def add_attr(self, name, value):
        self.top.add_attr(name, value)


    def set_attr(self, name, value):
        self.top.set_attr(name, value)


    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def get_style(self, name):
        self.top.get_style(name)



    def add_behavior(self, behavior):
        self.top.add_behavior(behavior)


    def add_color(self, name, palette_key, modifier=0, default=None):
        self.top.add_color(name, palette_key, modifier=modifier, default=default)


            
    def get_kwargs(self):
        return self.kwargs

    def get_sobject_from_kwargs(self):
        sobject = None

        search_key = self.kwargs.get('search_key')
        parent_key = self.kwargs.get('parent_key')
        # sometimes None is passed as a string
        if search_key == "None":
            return None

        if search_key:
            sobject = Search.get_by_search_key( search_key )
        elif parent_key:
            sobject = Search.get_by_search_key( parent_key )
        else:
            search_type = self.kwargs.get("search_type")
            code = self.kwargs.get("code")
            id = self.kwargs.get("id")
            if search_type and (code or id):
                search = Search(search_type)
                if code:
                    search.add_filter("code", code)
                    try:
                        id = int(code)
                        search.add_filter("id", id)
                        search.add_where("or")
                    except ValueError as e:
                        pass
                elif id:
                    try:
                        #id = int(code)
                        search.add_filter("id", id)
                    except ValueError as e:
                        pass
                        #search.add_filter("code", code)

                sobject = search.get_sobject()
        return sobject



    def serialize(self):
        '''provide the ability for a widget to serialize itself'''

        xml = Xml()
        xml.create_doc("config")

        # create the top element
        element = xml.create_element("element")
        xml.set_attribute(element, "name", self.name)

        # create the display handler
        display = xml.create_element("display")
        xml.set_attribute(display, "class", Common.get_full_class_name(self) )
        element.appendChild(display)

        # create the options
        for name, value in self.kwargs.items():
            if value:
                option = xml.create_text_element(name, value)
            else:  # avoid the \n in the textContent of the textNode 
                option = xml.create_element(name) 
            display.appendChild(option)

        return xml.to_string(element)


    def get_top(self):
        return self.top


    def add_style(self, name, value=None):
        return self.top.add_style(name, value=value)

    def add_class(self, class_name):
        return self.top.add_class(class_name)

    def has_class(self, class_name):
        return self.top.has_class(class_name)

    def add_behavior(self, behavior):
        return self.top.add_behavior(behavior)

    def add_relay_behavior(self, behavior):
        return self.top.add_relay_behavior(behavior)


    def set_option(self, name, value):
        self.kwargs[name] = value

    def get_option(self, name):
        return self.kwargs.get(name)

   

    def get_persistent_key(self):
        return "whatever"

    def commit(self):
        # store the widget persistently
        config_xml = self.serialize()
        key = self.get_persistent_key()
        WidgetSettings.set_key_values(key, [config.xml.to_string()])

    
    def get_by_key(self, key):
        key = self.get_persistent_key()
        return WidgetSettings.set_key_values(key, [config.xml.to_string()])


    def set_as_panel(self, widget, class_name='spt_panel', kwargs=None):
        self.top = widget

        widget.add_class(class_name)
        widget.add_attr("spt_class_name", Common.get_full_class_name(self) )

        if not kwargs:
            kwargs = self.kwargs
        for name, value in kwargs.items():
            if name == 'class_name':
                continue
            if value == None:
                continue
            elif isinstance(value, bool):
                if value == True:
                    value = 'true'
                else:
                    value = 'false'
            elif isinstance(value, SObject):
                value = value.get_search_key()
            elif not isinstance(value, basestring):
                value = str(value)
            # replace " with ' in case the kwargs is a dict
            value = value.replace('"', "'")
            if value:
                widget.add_attr("spt_%s" % name, value)

    def get_top_wdg(self):
        return self.top

    def process_state(state):
        '''process the state object for use with a widget. Usually a dictionary
           or a string version of it'''
        if not state:
            state = {}
        elif isinstance(state, basestring):
            # FIXME: SECURITY HOLE: NOT SURE ABOUT THIS
            if state != 'null':
                try:
                    state = eval(state)
                except Exception as e:
                    print("WARNING: ", str(e))
                    state = {}
        return state
    process_state = staticmethod(process_state)



