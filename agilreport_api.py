# -*- coding: utf-8 -*-
import datetime
import time 
import json
import collections
import copy
import os
import sys
from Agil_Template import Template
from Agil_Container import Container
from openerp.modules import module
sys.setrecursionlimit(10000)

#====================================================================
# Directories  
#CD_ODOO_ADDONS     = os.getcwd()+ '/'+"addons/" 
CD_STATIC_REPORTS  = module.get_module_path('report_def')+"/static/reports/" #CD_ODOO_ADDONS + "report_def/static/reports/"

def end_file(file_name,str_end):
    if file_name:
        if not file_name.endswith(str_end):
            file_name = file_name + str_end
        return file_name
    else:
        return None

def report_path_names(report,folder_template=None):
    
    env_vars = {}
    if folder_template == None: 
        folder_template = 'templates'
    env_vars['report_name'] = report.name
    env_vars['module_name'] = report.module_id.name
    env_vars['json_file_name']   = report.json_file_name
    env_vars['template_file_name'] = end_file(report.template_file_name,'.html')
    env_vars['template_html'] = folder_template
    env_vars['xml_file_name'] = end_file(report.xml_file_name,'.xml')  
    
    env_vars['path_json_file'] = CD_STATIC_REPORTS +env_vars['module_name']+"/" + env_vars['report_name']+"/JSON/"   
    env_vars['path_template_source'] =  module.get_module_path(env_vars['module_name'])  + "/" + folder_template + "/"
    env_vars['path_name_output'] = CD_STATIC_REPORTS + env_vars['module_name']+"/"+env_vars['report_name']+"/HTML/"
    env_vars['path_xml_report'] = CD_STATIC_REPORTS + env_vars['module_name']+"/"+env_vars['report_name']+"/report_def/"
    return env_vars


class oerp_report():
    
    def __init__(self,pool,cr,uid):
        self.pool = pool
        self.cursor = cr 
        self.uid = uid
            
    def declare_report(self,attributes):
        user = self.pool.get('res.users').browse(self.cursor,self.uid,self.uid)
        attributes['user'] =  user
        attributes['company'] = user.company_id
        attributes['cr'] = self.cursor
        attributes['pool'] = self.pool
        return current_report(attributes)
    
    
    def set_preview(self,cur_report):
        cur_report.output_file = cur_report.env_vars['json_file_name']
        container_file = cur_report.env_vars['path_name_output'] + end_file(cur_report.output_file,'.html')  
        #create new container
        cur_report.container_pages = Container(container_file)
        return cur_report.container_pages
    
    def to_preview(self,cur_report):
        #prepare template
        template = cur_report.json_out.get_template()
        template.__class__= Template
        
        #add template to container
        cur_report.container_pages.add(template)
        
        #save container 
        cur_report.container_pages.save()
        output_file_name = end_file(cur_report.output_file,'.html')
        
        self.pool.get("report.def").write(cur_report.cursor, 
                                          cur_report.user.id,
                                          [cur_report.report.id],
                                          {'out_template_file_name': output_file_name},
                                          context=None)
         
          
        return {
            'type' : 'ir.actions.client',
            'name' : 'Report Viewer Action',
            'tag' : 'report.viewer.action',
            'params' : {'report_id': cur_report.report.id,'json_id':cur_report.id_file},
         }
         
    def to_preview_bin(self,cur_report):
        #prepare template
        template = cur_report.json_out.get_template()
        template.__class__= Template
        report_request = self.pool.get("report.def.request")
        #add template to container
        cur_report.container_pages.add(template)
        
        return cur_report.container_pages.get_preview()
        
                
    def start_report(self,attributes):
        cur_report = self.declare_report(attributes)
        record_list = attributes.get('record_list',[])
        if attributes.get('bin_report',False):
            return self.prepare_report(cur_report,record_list)
        else:
            return self.set_report(cur_report,attributes.get('record_list',None))
    
    def prepare_report(self,cur_report,recordlist): 
        if cur_report.report: 
            result = cur_report.execute_query(recordlist)
            if cur_report.report.type == 'formulary':
                cur_report.print_record_list(result)
            else:
                cur_report.print_record_list(result)

            cur_report.json_out = json_to_report(cur_report)
            #print 'previewing report'
            cur_report.container_pages = self.set_preview(cur_report)
            return self.to_preview_bin(cur_report)
    
    def set_report(self,cur_report,recordlist):
        out_bin = self.prepare_report(cur_report,recordlist)
        if  out_bin:
            return report_request.set_action_request_report(cur_report.cursor,
                                                 cur_report.user.id, 
                                                 cur_report.report.id, 
                                                 out_bin,
                                                 context)



class ao_report_json_files(object):
    
    def __init__(self, dic_json):
        self.name = dic_json['name']
        self.report_id = dic_json['report_id']

class ao_json_xxxxxx(object):
    
    def __init__(self,cur_report):
        self.cur_report  = cur_report
        self.report_name = cur_report.report.name
        self.json_name   = self.get_file_name(cur_report)
        
    def save_file(self,cur_report):
        json_pool = cur_report.pool.get('report.def.json_files') 
        self.json_id = json_pool.create(cur_report.cursor,
                                        cur_report.user.id,
                                        {'name':self.json_name,
                                         'report_id':cur_report.report.id})
        return self.json_id
    
    
    def get_file_name(self,cur_report):
        # generate uniq Json file name 
        today     = datetime.datetime.now()
        time_now  = str(today.time())[0:8]
        report_name = cur_report
        cur_report.output_file = cur_report.env_vars['json_file_name'] + "_" + str(today.date()) + "_" + time_now 
        json_name   = end_file(cur_report.output_file,'.json')
        cur_report.path_json_file = cur_report.env_vars['path_json_file'] + json_name
        return json_name
    
        
    def to_file(self,cur_report):
        
        # Create path folder if necessary 
        # set and write json objet 
          
        report_pages = collections.OrderedDict()
        myreport     = collections.OrderedDict()
        report_pages['Pages']  = cur_report.pages 
        report_pages['Images'] = cur_report.images
        myreport['Report']     = report_pages
        
        # Creates the file directories for managing different types of report
        path_folder = CD_STATIC_REPORTS
        if self.create_folder(path_folder):
            pass 
        
        path_folder = path_folder + '/' + cur_report.env_vars['module_name'] + '/'
        if self.create_folder(path_folder):
            #folders to store html and pdf files
            if(self.create_folder(path_folder +  cur_report.env_vars['report_name'] )):
                self.create_folder(path_folder + cur_report.env_vars['report_name'] +'/HTML')
                self.create_folder(path_folder + cur_report.env_vars['report_name'] +'/PDF')
                #folder to store json files
                path_folder = path_folder + cur_report.env_vars['report_name'] +'/JSON/'
                if self.create_folder(path_folder):
                    file_name = path_folder + self.json_name
                    # Write JSON file from the object
                    with open(file_name, 'w') as json_file:
                        json.dump(myreport, json_file, indent=4)
        return self.json_name
     
    
    def create_folder(self, path_target):
        try:
            os.mkdir(path_target)
            return True
        except OSError:
            pass
            return True
    
#   
class json_to_report():
    
    
    def __init__(self,cur_report):
        self.html_template        = cur_report.env_vars.get('template_html', None) 
        self.path_template_source = cur_report.env_vars.get('path_template_source', None) 
        self.file_template        = cur_report.env_vars.get('template_file_name', None) 
        self.path_name_output     = cur_report.env_vars.get('path_name_output', None) 
       
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
        
        model_bloc = self.template.get_repeted_bloc() 
        count_bloc = cur_report.get_max_bloc_section('Details')
        self.template.copie_bloc({"class":"body_table"},count_bloc,model_bloc)
         
         
        nombre_page = len(cur_report.pages.keys())
        
        self.template.create_model_page()
        
        # remplacement de la copie de page     
        page_index = 0
        for page_key,page_value in cur_report.pages.iteritems():
            my_page = self.template.create_page_copy()
            #------------------section Report header ----------------------
            self.page_merge_section(self.template,my_page,page_value,cur_report.images,'Report_header')
            #------------------section Page Header ---------------------- 
            self.page_merge_section(self.template,my_page,page_value,cur_report.images,'Page_header')
            #------------------section Details --------------------------
            self.page_merge_section(self.template,my_page,page_value,cur_report.images,'Details')
            #------------------section Page footer ----------------------
            self.page_merge_section(self.template,my_page,page_value,cur_report.images,'Page_footer')
            #------------------section Report footer ----------------------
            self.page_merge_section(self.template,my_page,page_value,cur_report.images,'Report_footer')
            # add page 
            self.template.add_page(my_page)
            page_index += 1
        
        self.template.destroy_model_page()
        
        
    def page_merge_section(self,temp,my_page,page_value,images,report_section):
        if page_value.has_key(report_section):
            for key_bloc,val_bloc in page_value[report_section].iteritems():
                temp.page_set_section_values(my_page,report_section,images,key_bloc,val_bloc) 
    
    def read_json_file(self,path):
        data_file =""
        with open(path,'r+') as json_file:
            data_file = data_file + json_file.read()
            
        json_data = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(data_file)
        return json_data
    
    def get_template(self):
        return self.template

    def save_report(self):
        self.template.copie(self.path_name_output + self.file_template)
  

    
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
            self.col_sections = dic_report['col_sections']
            
            myKey = 'report_context'
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
        self.sequence = dic_field['sequence']
        self.section = dic_field['section']
        self.source_data = dic_field['source_data']
        self.field_type = dic_field['field_type']
        self.template_id = dic_field['template_id']
        self.expression = dic_field['expression']
        self.formula = dic_field['formula']
        self.function = dic_total['function']
        self.reset_after_print = dic_total['reset_after_print']
        self.reset_repeat_section = dic_total['reset_repeat_section']
 
    
class ao_report_json_files(object):
    
    def __init__(self, dic_json):
        self.name = dic_json['name']
        self.report_id = dic_json['report_id']


class report_total():
    def __init__(self,totals,section_names,deferred=False):
        self.cur_value = 0
        self.totals = totals
        self.deferred = deferred
    
        self.deferred_fileds = {}    
        self.reset_totals()

        for total in self.totals:
            if deferred:
                for field in section_names.values():
                    if total.total_field_id:
                        if total.total_field_id.id == field.id:
                            self.deferred_fileds[field.id] = total
                            
    def reset_totals(self):
        for total in self.totals:
            self.set_total(total.name,0)
        
    def sum(self,total_name, cur_val = None):
        if cur_val == None: 
            cur_val = self.cur_value  
        cur_total = getattr(self,total_name,0) 
        cur_total += cur_val
        self.set_total(total_name, cur_total)
        return cur_total
    
    def count(self,total_name,cur_val = 1):
        return self.sum(total_name, cur_val) 
    
    def average(self,total_name,cur_val=None):
        if cur_val == None: 
            cur_val = self.cur_value  
        cur_total = getattr(self,total_name,0) 
        cur_total = (cur_total + cur_val)/2
        self.set_total(total_name, cur_total)
        return cur_total
        
    def set_total(self, total_name,cur_val):
        setattr(self,total_name,cur_val)
    
    def get_value(self,total_name):
        return getattr(self,total_name,0)
    
    def reset_after_print(self,total):
        if total.reset_after_print:
            self.set_total(total.name,0)
    
    def get_deferred_totals(self,field_id):
        if self.deferred_fileds.has_key(field_id):
            return self.get_value(self.deferred_fileds[field_id].name)
        else:
            return ''
        
         
class current_report():
    
    def update_context(self, key_context, val_context):
        self.context[key_context] = val_context
        return self.context
    
    def dict_in_context(self,context):
        res = False
        for key,value in context.iteritems():
            if type(value) is dict:
                res = True
                break 
        return res
        
    
    def extend_context(self,my_context,result):
        is_dict = True
        while is_dict: 
            for key,value in my_context.iteritems():
                if type(value) is dict:
                    for dkey,dvalue in value.iteritems():
                         if not result.has_key(dkey):
                            result[dkey]= dvalue
                else:
                    result[key]= value
            
            is_dict = False 
            
        return result
    
         
        
    def __init__(self, context):
        self.initialize(context)
        
    def initialize(self, context):
        
        self.time = time.strftime("%H:%M:%S")
        self.now  = datetime.datetime.now()
        self.total_page = 0
        self.total_folio = 0
        self.report  = context.get('report',None)
        self.cursor  = context.get('cr',None)
        self.pool    = context.get('pool',None)
        self.user    = context.get('user',None)
        folder_template = context.get('folder_template','templates')
        user_context = context.get('context',None)
        self.company= context.get('company',None)
        self.form_data = context.get('datas',None)
        
        # init path files 
        self.env_vars = report_path_names(self.report,folder_template)

        self.pages = collections.OrderedDict()
        self.css_styles = collections.OrderedDict()
        self.images = collections.OrderedDict()
        self.page_number = 0
        self.page_folio  = 0 
        self.bloc_number = 1
        self.json_out = None
        self.id_file = None
        self.container_pages = None
        self.context = context
        for key,value in user_context.iteritems():
            self.context = self.update_context(key, value)
        
        self.glo_context = self.extend_context(self.context,{}) 
        self.context['current_report'] = self
        
        self.form_lst_fields = self.get_source_data_fields('Form')
        self.context_lst_fields = self.get_source_data_fields('Context')
        
        
        # report sections definitions
        self.section_names = { 'Report_header': self.get_section_fields('Report_header'),
                               'Page_header'  : self.get_section_fields('Page_header'),
                               'Details'      : self.get_section_fields('Details'),
                               'Page_footer'  : self.get_section_fields('Page_footer'),
                               'Report_footer': self.get_section_fields('Report_footer'),
                              }    
        # declare total function 
        self.total_functions = { 'Count':'count_total',
                                 'Sum':'sum_total',
                                 'Average':'average_total',
                                 }
        
        self.max_bloc_details = self.get_max_bloc_section('Details')
        
        self.globals = self.get_source_data_fields('Global')
        self.glo_fields = {}
        self.totals = self.get_source_data_fields('Total')       
        self.cur_total = report_total(self.totals,
                                      self.section_names['Details'],
                                      self.report.deferred_total)     
        self.context['total'] = self.cur_total
        self.key_group()
    
    
    def load_template(self):
        file_template =  self.env_vars['path_template_source'] + self.env_vars['template_file_name'] 
        my_template = Template()
        my_template.read(file_template)
        return my_template
                
    def query_prepare(self):
        query = self.report.query
        query = self.str_replace_values(self.form_lst_fields,'@form',query)
        query = self.str_replace_values(self.context_lst_fields,'@context',query)
        return query 
    
    def execute_query(self,lst_record = None): 
        # Execute query - if query is valid
        if self.report.type == 'normal':
            query = self.query_prepare()
            self.cursor.execute(query)
            return self.cursor.dictfetchall()
        elif self.report.type == 'user':
            return lst_record
        else: 
            return lst_record
        
    def str_replace_values(self,lst_fields,filter, str_query):
        for field in lst_fields:
            str_search = filter + '.' + field.name
            value = self.load_field_value(field)
            str_value = self.format_value(field,value)
            str_query = str_query.replace(str_search, str_value)
        return str_query
    
    def string_to_value(self,value,type = 'float'):
        n_value = 0
        if value:
            if isinstance(value,str):
                value = ''.join(value.split()).replace(',',".").replace('%','')
            try: 
               if type == 'float':
                   n_value = float(value)
               elif type in ['int','integer']:
                   n_value = int(value)
               else:
                   n_value = double(value)
            except ValueError:
               n_value = 0

        return n_value

    
    def format_value(self,field,value):
        if not value:
            value = '' 
        if field.field_type in ('Number','Double','Integer','List'):
            return str(value)
        else:
            return "'" + value + "'"
    
            
    def get_max_bloc_section(self, section_name):
        max_bloc = 1 
        for max_bloc_section in self.report.section_bloc_ids:
            if max_bloc_section.section == section_name:
                max_bloc = max_bloc_section.max_bloc_number
                break
        return max_bloc 
            
    def get_section_name(self, section_name):
        if self.section_names.has_key(section_name):
            return self.section_names[section_name]
    
    #def field_objectxxxxxxxxxxx(self, field_id, section_name='Details'):
    #    lst_fields = self.get_section_name(section_name)
        
    def number(self):
        return self.page_number
    
    def blocNumber(self):
        return self.bloc_number
    
    def date(self):
        return datetime.date.today()
    
    '''
    search field id in given bloc section name
    if exist return it's object field
    '''
    def field_object(self, field_id, section_name='Details'):
        section_list = self.get_section_fields(section_name)
        if section_list.has_key(field_id):
            field = section_list[field_id]
            return field
    
    '''
    
    '''
    def field(self, field_id, section_name='Details'):
        field = self.field_object(field_id, section_name)
        value = self.get_field(self.page_number, field.section, self.bloc_number, field.name)
        return value
    
    '''
        return field list of given section 
    '''
    def get_section_fields(self, section_name):
        section_list = {}
        for field in self.report.field_ids:
            if field.section == section_name:
                section_list[field.name] = field
        return section_list
    
    '''
       returns a list of matching fields, a given type of source_data  
    '''
    def get_source_data_fields(self, type_value):
        lst_fields = []
        for field in self.report.field_ids:
            if field.source_data == type_value:
                lst_fields.append(field)
        return lst_fields
    
    '''
        Regroupement et tri des records par cle
        pour constituer une liste des recodrs
    ''' 
    def sort_record_list(self,results):
       
        all_lists    = []
        key_name = ""
        key_list = {}
        self.set_global_list(results)
         
        if(self.field_key_group) and len(results)>0:
            key_name = self.field_key_group[0]
            for record in results:
                if key_list.has_key(record[key_name]):
                   lst_records = key_list[record[key_name]]  
                else:
                   lst_records=[] 
                   all_lists.append(lst_records)
              
                lst_records.append(record)
                key_list[record[key_name]] = lst_records 
                
            self.calculate_pages(all_lists)
        else:
            if len(results):
                all_lists.append(results)
                if self.max_bloc_details>0:
                    self.total_page = int(len(all_lists) /self.max_bloc_details) 
        return all_lists
    
    def calculate_pages(self,all_lists):
        cur_row  = 0
        self.total_page = 0
        self.total_folio = 0
      
        for list_record in all_lists:
            self.total_folio +=1
            self.total_page  +=1
            for record in list_record:
               cur_row +=1 
               if cur_row> self.max_bloc_details:
                   self.total_page +=1
                   cur_row = 1
                   
               
        
    def set_global_list(self,results):
        if len(self.globals)>0:
            for glofield in self.globals:
                if glofield.total_field_id and glofield.related_field_id:
                    self.glo_fields[glofield.name] = self.set_glo_field(results,
                                                                        glofield.total_field_id.name,
                                                                        glofield.related_field_id.name)
    
    def set_glo_field(self,results,cell_key,ref_key):
        recap = {}
        for record in results:
            if record.has_key(cell_key) and record.has_key(ref_key): 
                key_value = record[cell_key] 
                if not recap.has_key(key_value):
                    recap[key_value] = 0 
                recap[key_value] =  recap[key_value] + self.string_to_value(record[ref_key],'float')
        return recap 

    '''
     print a  list of records 
    '''
    def print_record_list(self,results):
        all_lists = self.sort_record_list(results)
        for list_record in all_lists:
            if self.report.reset_total_by_group:
                self.cur_total.reset_totals()
            self.page_folio  = 0     
            for record in list_record:
                self.print_line(record)
                
            self.print_end(record)
           
    '''
        print one record
    '''        
    def print_line(self,record):
        if self.bloc_number == 1:
            # create a new first page
            self.new_page(record,False)
        
        # checked if necessary to change page details
        if self.bloc_number >  self.max_bloc_details:
            self.end_page(record)
            # Create a next page
            self.new_page(record,True)
        
        # process body for any record
        self.evaluate_fields('Details',record)
        self.bloc_number += 1 
    
    '''
        Ends properly a footer. Evaluates if there are blocks to be printed before 
        reaching the end of the detail section. It prints the remaining blocks with null values 
        and prints the bottom of the page
    '''
    def print_end(self,record):
        if self.bloc_number <=  self.max_bloc_details:
            while self.bloc_number <= self.max_bloc_details:
                self.evaluate_fields('Details',False,False)
                self.bloc_number += 1 
                
            self.end_page(record)
    
    '''
        start a new page
        print Page Header and Report Header 
    '''
    def new_page(self, record,deferred = False):
        self.page_number += 1
        self.page_folio  += 1
        self.bloc_number = 1
        self.evaluate_fields('Report_header', record)
        self.evaluate_fields('Page_header', record)
        if deferred and self.cur_total.deferred:
            self.evaluate_fields('Details',record,True,True)
            self.bloc_number += 1
    '''
        ended page 
        print Page Footer and Report Footer
    '''
    def end_page(self, record):
        self.bloc_number = 1
        self.evaluate_fields('Page_footer', record)
        self.evaluate_fields('Report_footer', record)
    
    '''
        get css_Style of given page number
    '''
    def get_css_style_page(self, page_number):
        key_page = 'Page' + str(page_number)
        if not (self.css_styles.has_key(key_page)):
            self.css_styles[key_page] = collections.OrderedDict()
        return self.css_styles[key_page]

    '''
        get css_Style section of given page number and section
    '''
    def get_css_style_page_section(self, page_number, section_name):   
        mypage_style = self.get_css_style_page(page_number) 
        if not (mypage_style.has_key(section_name)):
            mypage_style[section_name] = collections.OrderedDict()
        return mypage_style[section_name]
    
    '''
        get section bloc of given page number,section, and bloc number
    '''
    def get_css_style_page_section_bloc(self, page_number, section_name, bloc_number):
        key_bloc = 'Bloc' + str(bloc_number)   
        mysection_style = self.get_css_style_page_section(page_number, section_name) 
        if not (mysection_style.has_key(key_bloc)):
            mysection_style[key_bloc] = collections.OrderedDict()
        return mysection_style[key_bloc]
    
        
    '''
        get page of given page number
    '''
    def get_page(self, page_number):
        key_page = 'Page' + str(page_number)
        if not (self.pages.has_key(key_page)):
            self.pages[key_page] = collections.OrderedDict()
        return self.pages[key_page]


    '''
        get section of given page number and section
    '''
    def get_page_section(self, page_number, section_name):   
        mypage = self.get_page(page_number) 
        if not (mypage.has_key(section_name)):
            mypage[section_name] = collections.OrderedDict()
        return mypage[section_name]
    
    '''
        get section bloc of given page number,section, and bloc number
    '''
    def get_page_section_bloc(self, page_number, section_name, bloc_number):
        key_bloc = 'Bloc' + str(bloc_number)   
        mysection = self.get_page_section(page_number, section_name) 
        if not (mysection.has_key(key_bloc)):
            mysection[key_bloc] = collections.OrderedDict()
        return mysection[key_bloc]
    
    '''
        set field value of given page number,section, bloc number and field_id
    '''
    def set_field(self, page_number, section_name, bloc_number, field_id, value): 
        mypage_section_bloc = self.get_page_section_bloc(page_number, section_name, bloc_number)
        mypage_section_bloc[field_id] = value
    
    '''
        get object field of given page number,section, bloc number and field_id
    '''
    def get_field(self, page_number, section_name, bloc_number, field_id): 
        mypage_section_bloc = self.get_page_section_bloc(page_number, section_name, bloc_number)
        if mypage_section_bloc.has_key(field_id):
            return mypage_section_bloc[field_id]
        else:
            return ''
    
    '''
        get a page section bloc
    '''
    def page_get_section_bloc(self, page_number, section_name, bloc_number):
        return self.get_page_section_bloc(page_number, section_name, bloc_number)
    
    '''
        not used yet 
    '''
    def get_value_from_bloc(self, bloc_values, field_id):
        if bloc_values.has_key(field_id):
            return bloc_values.has_key[field_id]
        else:
            return ' '
        
    
    '''
    '''    
    def key_group(self):
        self.field_key_group = []
        for section_name in self.section_names:
            section_list = self.get_section_fields(section_name)
            for key_name,field in section_list.items():
                if field.group == True:
                    self.field_key_group.append(field.name)
        return self.field_key_group
    
    '''
    '''
    def key_group_value(self,record):
        ref_value = ''
        for field in self.field_key_group:
            value = self.load_field_value(field,record)
            ref_value = ref_value + value
        return ref_value
     
    '''
       for a given section, all fields total type are calculated first
       Then fields are evaluated and retrieve their values
    '''
    def evaluate_fields(self, section_name, record=False,val_format=True,deferred=False):
        
        section_list = self.get_section_fields(section_name)
        mypage_section_bloc = self.get_page_section_bloc(self.page_number, 
                                                         section_name, 
                                                         self.bloc_number)
            
        #mysection_page = self.get_page_section(self.page_number, section_name)
        for key_name, field in section_list.items():
            
            if deferred:
                value = self.cur_total.get_deferred_totals(field.id)
                if self.report.deferred_label_field:
                    if field.id == self.report.deferred_label_field.id:
                        value = self.report.deferred_label
            else:
                value = self.load_field_value(field, record)
                value = self.calculate_field_value(field, value)
                self.formula_execute(field,value)
            
            if val_format and value:
                value = self.format_field_value(field,value)

            mypage_section_bloc[field.name] = value
            
    '''
        the field formula execution
    '''
    def formula_execute(self,field,value): 
       
        if field.formula:
            self.cur_total.cur_value = self.string_to_value(value,'float') 
            
            try:
                exec(field.formula, self.context)
            except SyntaxError:
                print 'Formula Error ', field.formula

    '''
        the field value is extracted from the current record
    '''
    def value_from_model(self, field, record):
        if record.has_key(field.name):
            return record[field.name]
        else:
            return 'error field ' + field.name
    
    '''
        the field value is extracted from the context
    '''
    def value_from_context(self,field,record): 
        value = ''
        if field:
            if field.expression:
                try:
                    value = eval(field.expression, self.context)
                except SyntaxError:
                    value = ''
            elif field.source_data == 'Global' and self.glo_fields.has_key(field.name):
                dic_value = self.glo_fields.get(field.name,{})
                if field.total_field_id:
                    key_name = field.total_field_id.name
                    key_value = self.load_field_value(field.total_field_id, record)
                    if dic_value.has_key(key_value):
                        value = dic_value[key_value]
                    
            else:
                value = self.glo_context.get(field.name,'')
        return value 
    
    '''
        the field value is extracted from the current form
    '''
    def value_from_form(self, field):
        if self.form_data.has_key(field.name):
            return self.form_data[field.name]
        else: 
            return 'error value from form : ' + field.name
    
    '''
        the field value is extracted from a total
        the total method reset are evaluated 
    '''
    def value_from_total(self, field):
        
        value = self.cur_total.get_value(field.name)
        self.cur_total.reset_after_print(field)
        return value
    
    '''
       the field value is extracted according its data source
    '''
    def load_field_value(self, field, record=False):
        value = ''
        if record and field.source_data == 'Model':
            return self.value_from_model(field, record)
                
        if field.source_data == 'Form':
            return self.value_from_form(field)
        elif field.source_data in ['Context','Global']:
            return self.value_from_context(field,record)
        elif field.source_data == 'Total':
            return self.value_from_total(field)
            
        return value
    
    def format_field_value(self,field,value):
        if field.field_format_id and field.field_format_id.format:
            if field.field_type in ('Number','Double','Integer','Currency'):
                amount = self.string_to_value(value,'float')
                str_format = str(field.field_format_id.format)
                return str_format.format(amount)
            #('String', 'List','Dict','Date','Time','Image','Static Image')
        return value
            
        
    '''
       the field value is extracted from stored static images   
    '''
    def field_static_image(self, field, value):
        if not self.images.has_key(field.name): 
            self.images[field.name] = value
        return 'StaticImage'
    
    '''
        part of the code reserved for the injection of values by external methods (python, html ...)
    '''
    def calculate_field_value(self, field, value):
        
        if field.source_data == 'Page':
            return self.page_number
       
        elif field.source_data == 'Page':
            return self.total_page
       
        elif field.source_data == 'Folio':
            return self.page_folio
        
        elif field.source_data == 'Folios':
            return self.total_folio
        
        elif field.source_data == 'Function':
            return 'my_function'
        
        elif field.source_data == 'Computed':
            return eval(field.expression, self.context)
        
        elif field.source_data == 'Html':
            return 'my_html'
        
        elif field.field_type == 'Static Image':
            return self.field_static_image(field, value)
        return value
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
