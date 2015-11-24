# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as soup
import os
import sys
import pdfkit
import copy
sys.setrecursionlimit(10000)

class Template(object):
    
    def __init__(self,src_path=None):
        self.content_html = None
        self.report_template = None
        if(src_path):
            self.content_html = self.read(src_path)
            self.report_template = self.content_html.find(attrs={"class":"Page"})
    '''
        Read template
    '''    
    def read(self,src_path):
        with open(src_path, 'r+') as template_file:
            self.file_content = template_file.read()
        self.content_html=soup(self.file_content,"lxml")
        self.report_template = self.content_html.find(attrs={"class":"Page"})
    '''
        affecte une page html comme model
    '''    
    def set_content_html(self,page_content):
        self.content_html = soup(page_content,"lxml")
        self.report_template = self.content_html.find(attrs={"class":"Page"})   
        return self.content_html      
  
    '''
        Enregistrement de la template en cours
    '''
    def copie(self,dest_path):
        with open(dest_path, 'w+') as template_file:
            template_file.write(self.content_html.encode("utf-8"))
    
    '''
        Enregistrement de la template sous format Pdf 
    '''
    def save_pdf_from_file(self,input,output,orientation='portrait'):
        options = {
                'page-size':'A4',
                'margin-top':'0cm',
                'margin-right':'0cm',
                'margin-bottom':'0cm',
                'margin-left':'0cm',
                'orientation':orientation,    
                'print-media-type':'',
    
        }
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        return pdfkit.from_file(input,output,options=options,configuration=config)
    
    '''
       save pdf from string FIXME replace pdfkit.from_file by pdfkit.from_string
    '''
    def save_pdf_from_string(self,input,output,orientation='portrait'):
        options = {
                'page-size':'A4',
                'margin-top':'0cm',
                'margin-right':'0cm',
                'margin-bottom':'0cm',
                'margin-left':'0cm',
                'orientation':orientation,    
                'print-media-type':'',
        }
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        pdfkit.from_string(input,output,options=options,configuration=config)
    
    
    '''
       return paper format of the report
    '''
    def get_format(self):
        report = self.content_html.find(id="Report")
        return report["format"]
    '''
       return definition report
    '''
    def get_definition_report(self,def_report):
        report = self.content_html.find(id="Report")
        try:
            def_report['format'] = report['format'] or "Landscape"
            def_report['name']   = report['ao-name'] or False
            def_report['title']  = report['ao-title'] or False
            return def_report
        except:
            return def_report
    '''
        get the html section code
    '''
    def get_section(self,section_name):
        return self.report_template.find(attrs={"class":section_name})
    
    '''
        return the maxbloc section repeted bloc number 
    '''
    def get_max_bloc_section(self,section_name):
        section_tag=self.get_section(section_name)
        if(section_tag.has_key('ao-max-bloc')):
            return section_tag['ao-max-bloc']
        return "1"        
    
    def get_ids_bloc(self,bloc):
        fields={}
        field={}
        for element in bloc.find_all(id=True):
            field_name=element['id']
            source_data = "Model"
            type_data   = "String"
            if(element.has_key('ao-data-source')):
                source_data=element['ao-data-source']
            if(element.has_key('ao-type')):
                type_data=element['ao-type']
            
            field[field_name]={'source_data':source_data,'type':type_data}
        return field
        
    def get_class_section(self,section_name,class_name):
        section_tag = self.get_section(section_name)
        return section_tag.find_all(attrs={"class":class_name})
    
    '''
        return list of all template ids
    '''
    
    def get_ids_section(self,section_name):
        section_tag = self.get_section(section_name)
        return self.get_part_ids(section_tag)
    
    '''
        return list of all template ids
    '''
    def get_all_ids(self):
        return self.get_part_ids(self.report_template)
   
    '''
        return list of part of the template ids
    '''
    def get_part_ids(self,temp_part):
        ids=[]
        for element in temp_part.find_all(id=True):
            ids.append(element['id'])
        return ids
    
    '''
        return repeted bloc ids
    '''
    def get_ids_repeted_bloc(self):
        repeted_bloc = self.report_template.find(attrs={"type":"repeted_bloc"})
        return self.get_part_ids(repeted_bloc)
         
        
    def get_element_tag(self,tag_name):
        return self.report_template.find_all(tag_name)
    
    def get_element_id(self,id_name):
        if self.report_template:
            elet = self.report_template.find(id=id_name)
            if elet :
                return elet
            else:
                return False
    
    
    def get_element_class(self,class_name):
        if self.report_template:
            return self.report_template.find_all(attrs={'class':class_name})
        
    def get_element_attribute(self,attribute_name,attribute_value):
        if self.report_template:
            return self.report_template.find_all(attrs={attribute_name:attribute_value})
        
    def get_value_element(self,element):
        return element.string
    
    def set_value_element(self,element,value):
        element.string = value
    
    def set_value_id(self,id_name,value,type_elem):
        if self.report_template:
            element=self.report_template.find(attrs={'id':id_name})
            element['type']=type_elem    
            element.string=value
        
    def get_repeted_bloc(self):
        return copy.deepcopy(self.report_template.find(attrs={"type":"repeted_bloc"}))
    
     
    def get_max_bloc(self,bloc_repeted):
        try:
            return bloc_repeted['max_bloc']
        except:
            return None
        
    def get_footer_bloc(self,bloc_repeted):
        try:
            class_name=bloc_repeted['footer_bloc']
            return self.report_template.find(attrs={"class":class_name})
        except:
            return None
    
    def get_tag_head(self):
        tag_head=copy.deepcopy(self.content_html.find("head"))
        return tag_head
   
        
    def is_multi_page(self):
        if(self.report_template.find(attrs={"type":"repeted_bloc"}).clear()):
            return True
        return False
    
    def duplicate_page(self,count_page):
        modele_page = copy.deepcopy(self.content_html.find(attrs={"class":"Page_container"}))
        self.content_html.find(id="Report").clear()
        for i in xrange(0,count_page,1):
            copy_page=copy.deepcopy(modele_page)
            self.content_html.find(id="Report").append(copy_page)
            self.content_html.find(id="Report").append(self.content_html.new_tag("br"))
            del copy_page
        del modele_page
        
    def duplicate_bloc(self,page_index,count_bloc,modele_bloc,footer_bloc=None):
        pages = self.content_html.find_all(attrs={"class":"body_table"})
        pages[page_index].clear()
        for i in xrange(0,count_bloc,1):
            mb=copy.deepcopy(modele_bloc)
            pages[page_index].append(mb)
            del mb
            
        if(footer_bloc!=None):
            fb = copy.deepcopy(footer_bloc)
            pages[page_index].append(fb)
            del fb
        
        if(self.content_html.find(attrs={"class":"pagination"})):
            pag=self.content_html.find_all(attrs={"class":"pagination"})
            if(pag[page_index]):
                pag[page_index].string=str(page_index+1)
                
    def copie_bloc(self,find_elet,count_bloc,model_bloc):
        
        # find_elet = {"class":"body_table"}
        list_elets = self.content_html.find_all(attrs=find_elet)
        if list_elets:
            list_elets[0].clear()
            for i in xrange(0,count_bloc,1):
                mb = copy.deepcopy(model_bloc)
                mb['class']='Bloc'+str(i+1)
                list_elets[0].append(mb)
                del mb
            
                
    def set_val_bloc_repeted(self,page_index,values_id):
        pages=self.content_html.find_all(attrs={"class":"Page"})
        blocs_page=pages[page_index].find_all(attrs={"type":"repeted_bloc"})
        
        for key,value in values_id.iteritems():
            for id_bloc in blocs_page[key].find_all(id=True):
                if(value.has_key(id_bloc['id'])):
                    id_bloc.string=str(value[id_bloc['id']]) 
    
    def set_values_section(self,page_index,section_name,images,key_bloc,values_bloc):
        
        pages = self.content_html.find_all(attrs={"class":"Page"})
        section = pages[page_index].find(attrs={"class":section_name})
        blocs = section.find_all(attrs={"class":key_bloc})
        for bloc in blocs:
            if(bloc):
                for key,value in values_bloc.iteritems():
                    if(bloc.find(id=key)):
                        if(bloc.find(id=key).name=="img"):
                            tag_img=bloc.find(id=key)
                            tag_img["src"]="data:image/jpeg;base64,"+str(images[key])
                        else:
                            bloc.find(id=key).string=str(value).encode("utf-8")
    
    
    def get_data_template(self):
        
        sections = ['Report_header','Page_header','Details','Page_footer','Report_footer']
        template_def = {}
        
        for section_name in sections:
            template_def[section_name]={'max_bloc':self.get_max_bloc_section(section_name),'fields':{}}
            
            section = self.get_section(section_name)
            if(section.find(attrs={'class':'Bloc1'})):
                bloc=section.find(attrs={'class':'Bloc1'})
                template_def[section_name]['fields'] = dict(self.get_ids_bloc(bloc))
        return template_def
    
    def set_val_attr(self,attribute,attribute_value,new_value):
        if self.report_template:
            element=self.content_html.find(attrs={attribute:attribute_value})
            element[attribute]=new_value
    def remove_attr(self,element,attr_name):
        try:
            del element.attrs[attr_name]
            return True
        except:
            return False

    def set_attr(self,element,attr_name,new_attr_name,attr_value):
        if(self.remove_attr(element,attr_name)):
            self.add_attr(element,new_attr_name,attr_value)
            return True
        else:
            return False

    def add_attr(self,element,attr,value):
        if(element):
            element[attr]=value
            return True
        else:
            return False