# -*- coding: utf-8 -*-
import datetime
import json
import collections
import copy
import os

from Agil_Template import Template

class json_to_report():
    
    
    def __init__(self,attributes):
        
        self.path_json_file = attributes.get('path_json_file', None) 
        self.html_template  = attributes.get('html_template', None) 
        self.path_template_source = attributes.get('path_template_source', None) 
        self.file_template    = attributes.get('file_template', None) 
        self.path_name_output = attributes.get('path_name_output', None) 
       
        if self.path_template_source == None:
            self.path_template_source = os.getcwd()+ '/'
            
        if self.path_name_output == None:
            self.path_name_output = os.getcwd()+ '/'
            
        
        self.template = Template()
        if self.file_template:
            self.template.read(self.path_template_source + self.file_template)
        else:
            if self.html_template:
                self.template.set_content_html(self.html_template)
        
        modele_bloc = copy.deepcopy(self.template.get_repeted_bloc())
        footer_bloc_repeted = None
        if(self.template.get_footer_bloc(self.template.get_repeted_bloc()) != None):
            footer_bloc_repeted = copy.deepcopy(self.template.get_footer_bloc(self.template.get_repeted_bloc()))
        
        self.data = self.read_json_file(self.path_json_file)
        pages     = self.data["Report"]["Pages"]
        nombre_page = len(pages.keys())
        self.template.duplicate_page(nombre_page)
        
        page_index = 0
        for page_key,page_value in pages.iteritems():
            #------------------section Report header ----------------------
            self.data_merge_section(self.template,page_index,page_value,'Report_header')
            
            #------------------section Page Header ---------------------- 
            self.data_merge_section(self.template,page_index,page_value,'Page_header')
             
            #------------------section Details ----------------------
            nbr_bloc = len(pages[page_key]["Details"].keys())
            self.template.duplicate_bloc(page_index,nbr_bloc,modele_bloc,footer_bloc_repeted)
            page_values = {}
            k=0
            for key_bloc,val_bloc in page_value["Details"].iteritems():
                page_values[k]=val_bloc
                k+=1
            self.template.set_val_bloc_repeted(page_index,page_values)
         
            #------------------section Page footer ----------------------
            self.data_merge_section(self.template,page_index,page_value,'Page_footer')
             
            #------------------section Report footer ----------------------
            self.data_merge_section(self.template,page_index,page_value,'Report_footer')
                
            #---------------------------------------------------------
            page_index=page_index+1
        self.template.copie(self.path_name_output + self.file_template)
       # self.template.save_pdf_from_file(self.path_name_output + self.file_template, self.path_name_output + 'pos_order_details.pdf')
        
        
    
    def data_merge_section(self,temp,page_index,page_value,report_section):   
        for key_bloc,val_bloc in page_value[report_section].iteritems():
            temp.set_values_section(page_index,report_section,val_bloc) 
        
    def read_json_file(self,path):
        data_file =""
        with open(path,'r+') as json_file:
            data_file = data_file + json_file.read()
            
        json_data = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(data_file)
        return json_data
    

class ao_report(object):
    
    def __init__(self, dic_report=None):
        if dic_report:
            
            self.name = dic_report['name']
            self.title = dic_report['title']
            
            self.module_id = dic_report['module_id']
            self.query = dic_report['query']
            self.format = dic_report['format']
            self.type = dic_report['type']
            
            self.template_html = dic_report['template_html']
            self.template_file_name = dic_report['template_file_name']
            self.json_file_name = dic_report['json_file_name']
            
            self.col_fields = dic_report['col_fields']
            self.col_totals = dic_report['col_totals']
            self.col_sections = dic_report['col_sections']
            
            myKey='report_context'
            if dic_report.has_key(myKey):
                self.report_context = dic_report[myKey]
            else:
                self.report_context = {}
            
            
            
  
    def add_fields(self, obj_field):
        self.field_ids[obj_field.name] = obj_field
    
    def add_col_fields(self, colfields):
        for field in colfields:
            self.add_fields(field)
            
    def add_sections(self, obj_section):
        self.section_bloc_ids[obj_section.name] = obj_section
    
    def add_col_sections(self, colsections):
        for obj_section in colsections:
            self.add_sections(obj_section)
            
    def add_totals(self, obj_total):
        self.col_section_blocs[obj_total.name] = obj_total
    
    def add_col_totals(self, coltotals):
        for obj_total in coltotals:
            self.col_totals(obj_total)

class ao_report_section_bloc(object):
    
    def __init__(self, dic_section):
        self.report_id = dic_section['report_id']
        self.section = dic_section['section']
        self.max_bloc_number = dic_section['max_bloc_number']

class ao_report_def_field(object):
    
    def __init__(self, dic_field):
        self.template_id = dic_field['template_id']
        self.name = dic_field['name']
        self.report_id = dic_field['report_id']
        self.total_id = dic_field['total_id']
        self.sequence = dic_field['sequence']
        self.section = dic_field['section']
        self.source_data = dic_field['source_data']
        self.field_type = dic_field['field_type']
        self.template_id = dic_field['template_id']

class ao_report_field_total(object):
    
    def __init__(self, dic_total):
        self.name = dic_total['name']
        self.report_id = dic_total['report_id']
        self.function = dic_total['function']
        self.reset_after_print = dic_total['reset_after_print']
        self.reset_repeat_section = dic_total['reset_repeat_section']
        self.field_ids = dic_total['field_ids']
    
class ao_report_json_files(object):
    
    def __init__(self, dic_json):
        self.name = dic_json['name']
        self.report_id = dic_json['report_id']

class py_report():
    
    def init_class(self, cursor, datas, report, company, user): 
        self.cursor = cursor
        self.user_id = user.id
        ao_api = ao_report_api()
        return ao_api.init_class(self.cursor, datas, report, company, user)
  

class ao_report_api():
    
    def init_class(self, cursor, datas, report, company, user):

        self.user_id = user.id 
        self.result = {}
        self.report_context = {}
        self.cursor = cursor
        report_name = report.name
        
        self.report_context = self.update_context('report', report)
        self.report_context = self.update_context('company', company)
        self.report_context = self.update_context('user', user)
        self.report_context = self.update_context('datas', datas)
    
    
        # Execute query
        cur_report = current_report(self.report_context)
        query = cur_report.replace_form_values(cur_report.report.query)
        self.cursor.execute(query)
        self.result = self.cursor.dictfetchall() 
         
        max_bloc_details = cur_report.get_max_bloc_section('Details')
        
        for record in self.result:
         
            # process Heard first time
            if cur_report.page_number == 0:
                # create a new page
                cur_report.new_page(record)
                 
            # process body for any record      
            cur_report.evaluate_fields('Details', record)
            cur_report.bloc_number += 1 
            
            # process footer only after the last bloc  
            # FIXME
            if cur_report.bloc_number > max_bloc_details:
                cur_report.bloc_number = 1 
                # end of page
                cur_report.end_page(record)
                # Create a next page
                cur_report.new_page(record)
                
        if (cur_report.page_number > 0):
            cur_report.bloc_number = 1 
            cur_report.end_page(record)
            
        return cur_report
    
    def update_context(self, key_context, val_context):
        self.report_context[key_context] = val_context
        return self.report_context
    
    def raz_totals(self, totals):
        for total in totals:
            self.set_total(total, 0)
        return True
    
    def fill_all_json_data(self, json_data):
        json_report = json_data['Report']
        json_pages = json_report['Pages']
        my_temple = Template(page)
        html_report = my_temple.create_new_report()
        for key_page, my_page in json_pages.items():
            page_number = int(key_page.replace('Page', ''))
            my_temple.fill_create_new_page(page_number) 
            for key_section, my_section in my_page.items():
                
                for key_bloc, my_bloc in my_section.items():
                    bloc_number = int(key_page.replace('Bloc', ''))
                    for field, value in my_bloc.items():
                        self.fill_field_value(key_section, page_number, bloc_number, field, value)
    
    def fill_field_value(self, key_section, page_number, bloc_number, field, value):
        return ' '
        
                    
class current_page():
    def __init__(self, cur_report):
        self.my_page = cur_report
        
class current_report():
    
    def __init__(self, context):
        
        self.pages = collections.OrderedDict()
        self.totals = {}
        self.images = collections.OrderedDict()
        self.page_number = 0
        self.report = context['report']
        self.form_data = context['datas']
        self.bloc_number = 1
        self.context = context
        self.context['current_report'] = self
        
        self.form_lst_fields = self.form_fields('Form')
        
        self.section_names = { 'Report_header': self.get_section_fields('Report_header'),
                               'Page_header'  : self.get_section_fields('Page_header'),
                               'Details'      : self.get_section_fields('Details'),
                               'Page_footer'  : self.get_section_fields('Page_footer'),
                               'Report_footer': self.get_section_fields('Report_footer'),
                              }    
        
        tot_function = self.total_calculate
        self.total_functions = { 'Count':'count_total',
                                 'Sum':'sum_total',
                                 'Average':'average_total',
                                 }
        self.init_totals()
    
    
    def get_max_bloc_section(self, section_name):
        max_bloc = 1 
        for max_bloc_section in self.report.section_bloc_ids:
            if max_bloc_section.section == section_name:
                max_bloc = max_bloc_section.max_bloc_number
                break
        return max_bloc 
            
        
    
    def init_totals(self):
        '''
         create totals for current report and reset totals for all methods
        '''
        for total in self.report.total_ids:
            my_total = {}
            my_total['name'] = total.name
            my_total['function'] = total.function
            my_total['method'] = self.total_functions.get(total.function, 'Sum') 
            my_total['reset_after_print'] = total.reset_after_print
            my_total['reset_repeat_section'] = total.reset_repeat_section
            self.totals[total.name] = self.reset_total(my_total)
            
    def total_calculate(self, field, value):
        total_name = field.total_id.name
        my_total = self.totals[total_name]
        if my_total['function'] == 'Sum':
                my_total['total'] = my_total['total'] + value
        
        if my_total['function'] == 'Count':
            my_total['total'] = my_total['total'] + 1
        
        if my_total['function'] == 'Average':
            my_total['total'] = (my_total['total'] + value) / 2 
  
        self.totals[total_name] = my_total 
        
    def reset_total(self, my_total):
        '''
        reset totals for given total and a list functions
        '''
        my_total['total'] = 0
        return my_total
      
    def get_section_name(self, section_name):
        if self.section_names.has_key(section_name):
            return self.section_names[section_name]
    
    def field_objectxxxxxxxxxxx(self, field_id, section_name='Details'):
        lst_fields = self.get_section_name(section_name)
        
    def number(self):
        return self.page_number
    
    def blocNumber(self):
        return self.bloc_number
    
    def date(self):
        return datetime.date.today()
    
    def field_object(self, field_id, section_name='Details'):
        section_list = self.get_section_fields(section_name)
        if section_list.has_key(field_id):
            field = section_list[field_id]
            return field
    
    def field(self, field_id, section_name='Details'):
        field = self.field_object(field_id, section_name)
        value = self.get_field(self.page_number, field.section, self.bloc_number, field.name)
        return value
    
    def get_section_fields(self, section_name):
        section_list = {}
        for field in self.report.field_ids:
            if field.section == section_name:
                section_list[field.name] = field
        return section_list
    
    def form_fields(self, type_value):
        lst_fields = []
        for field in self.report.field_ids:
            if field.source_data == type_value:
                lst_fields.append(field)
        return lst_fields
    
    def new_page(self, record):
        self.page_number += 1
        self.evaluate_fields('Report_header', record)
        self.evaluate_fields('Page_header', record)
        
    def end_page(self, record):
        self.evaluate_fields('Page_footer', record)
        self.evaluate_fields('Report_footer', record)
    
    def replace_form_values(self, str_query):
        
        for parm in self.form_lst_fields:
            str_search = '@form.' + parm.name
            str_value = "'" + self.value_from_form(parm.name.rstrip()) + "'"
            str_query = str_query.replace(str_search, str_value)
        return str_query
    
    def get_page(self, page_number):
        key_page = 'Page' + str(page_number)
        if not (self.pages.has_key(key_page)):
            self.pages[key_page] = collections.OrderedDict()
        return self.pages[key_page]

    def get_page_section(self, page_number, section_name):   
        mypage = self.get_page(page_number) 
        if not (mypage.has_key(section_name)):
            mypage[section_name] = collections.OrderedDict()
        return mypage[section_name]
    
    def get_page_section_bloc(self, page_number, section_name, bloc_number):
        key_bloc = 'Bloc' + str(bloc_number)   
        mysection = self.get_page_section(page_number, section_name) 
        if not (mysection.has_key(key_bloc)):
            mysection[key_bloc] = collections.OrderedDict()
        return mysection[key_bloc]
    
    def set_field(self, page_number, section_name, bloc_number, field_id, value): 
        mypage_section_bloc = self.get_page_section_bloc(page_number, section_name, bloc_number)
        mypage_section_bloc[field_id] = value
    
    def get_field(self, page_number, section_name, bloc_number, field_id): 
        mypage_section_bloc = self.get_page_section_bloc(page_number, section_name, bloc_number)
        if mypage_section_bloc.has_key(field_id):
            return mypage_section_bloc[field_id]
        else:
            return ''
    
    def page_get_section_bloc(self, page_number, section_name, bloc_number):
        mypage_section_bloc = self.get_page_section_bloc(page_number, section_name, bloc_number)
        return mypage_section_bloc
    
    def get_value_from_bloc(self, bloc_values, field_id):
        if bloc_values.has_key(field_id):
            return bloc_values.has_key[field_id]
        else:
            return ' '
        
    def to_json(self, file_name, rep):
        report_pages = collections.OrderedDict()
        myreport = collections.OrderedDict()
        
        report_pages['Pages'] = self.pages 
        report_pages['Images'] = self.images
        myreport['Report'] = report_pages
        path_folder = os.getcwd() + '/openerp/addons/report_def_store/static/reports'
        if self.create_folder(path_folder):
            pass 
        path_folder = path_folder + '/' + rep.module_id.shortdesc
        if self.create_folder(path_folder):
            path_folder = path_folder + '/' + self.report.name
            if self.create_folder(path_folder):
                file_name = path_folder + '/' + file_name
                with open(file_name, 'w') as json_file:
                    json.dump(myreport, json_file, indent=4)
        return myreport 
    
    def create_folder(self, path_target):
        try:
            os.mkdir(path_target)
            return True
        except OSError:
            pass
            return True
 
    def evaluate_fields(self, section_name, record):
        
        section_list = self.get_section_fields(section_name)
        mysection_page = self.get_page_section(self.page_number, section_name)
        for key_name, field in section_list.items():
            value = self.load_field_value(field, record)
            self.set_field(self.page_number, field.section, self.bloc_number, field.name, value)
            if field.total_id and field.source_data != 'Total':
                self.total_calculate(field, value)
                
        for key_name, field in section_list.items():
            value = self.get_field(self.page_number, field.section, self.bloc_number, field.name)
            value = self.calculate_field_value(field, value)
            self.set_field(self.page_number, field.section, self.bloc_number, field.name, value)
    
    def value_from_model(self, field, record):
        if record.has_key(field.name):
            return record[field.name]
        else:
            return 'error field' + field.name
    
    def value_from_form(self, field_id):
        if self.form_data.has_key(field_id):
            return self.form_data[field_id]
        else: 
            return 'error form data' + field_id
    
    def value_from_total(self, field):
        value = ''
        if field.total_id:
            my_total = self.totals[field.total_id.name]
            value = my_total['total']
            if my_total['reset_after_print']:
                self.totals[my_total['name']] = self.reset_total(my_total)
                
        return value
    
    def load_field_value(self, field, record):
        value = ''
        if field.source_data == 'Model':
            value = self.value_from_model(field, record)
            
        if field.source_data == 'Form':
            value = self.value_from_form(field.name)
        
        if field.source_data == 'Total':
            value = self.value_from_total(field)
            
        return value
    
    def field_static_image(self, field, value):
        
        if field.field_type == 'Static Image':
            if not self.images.has_key(field.name): 
                self.images[field.name] = value
            value = 'StaticImage'
            
        return value
       
    def calculate_field_value(self, field, value):

        if field.source_data == 'Function':
            value = 'my_function'
        
        if field.source_data == 'Computed':
            value = eval(field.expression, self.context)
        
        if field.source_data == 'Html':
            value = 'my_html'
        
        value = self.field_static_image(field, value)
        return value

    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
