# -*- coding: utf-8 -*-
import pdfkit
from bs4 import BeautifulSoup as soup
from Agil_Template import Template
import copy
class Container_doc(object):
    
    def __init__(self,template,sequence,doc_type):
        template.__class__=Template
        content=template.content_html
        content_pages=content.find_all(attrs={'class':'Page_container'})
        for page in content_pages:
            page['format']=doc_type
        self.content = content_pages
        self.doc_type = doc_type
        self.sequence = sequence
    
class Container(object):
    
    def __init__(self,file_name=None):
        self.col_docs = {}
        self.sequence = 0 
        self.file_name = file_name
    
    def add(self,template,doc_type = 'portrait'):
        template.__class__=Template
        new_doc = Container_doc(copy.deepcopy(template),self.sequence,template.get_format())
        self.sequence = self.sequence + 1
        self.col_docs[self.sequence] = new_doc
        
    def save(self,doc_type = 'portrait',file_name = None):
        if(self.file_name==None):
            self.file_name=file_name
        str_file = soup("""<!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8"  />
                    <script type="text/javascript" src="../inclu/jquery.js" ></script>
                    <script type="text/javascript" src="../inclu/etat_script.js" ></script>
                </head>
                <body id="viewer">
                    <!-- Debut de Rapport -->
                    <div id="Report" format="portrait">
                        
                    </div>
                    <!-- Fin de Rapport -->
                </body>
            </html>
            """)
        
        for seq,doc in self.col_docs.iteritems():
#            if doc.doc_type == doc_type or doc_type =='all':
            for content_element in doc.content:
                str_file.find(id='Report').append(content_element)
                str_file.find(id='Report').append(str_file.new_tag("br"))
        if str_file:     
            if self.file_name != None: 
                with open(self.file_name, 'w+') as container_file:
                    container_file.write(str_file.prettify())

    def save_pdf_from_file(self,input,output,orientation='portrait'):
        options = {
                'zoom':'0.8',
                'margin-top':'10mm',
                'margin-bottom':'0.0mm',
                'orientation':orientation,    
                'print-media-type':'',
    
        }
        pdfkit.from_file(input,output,options=options)
    
    def save_pdf_from_string(self,input,output,orientation='portrait'):
        options = {
                'zoom':'0.8',
                'margin-top':'10mm',
                'margin-bottom':'0.0mm',
                'orientation':orientation,    
                'print-media-type':'',
        }
        pdfkit.from_string(input,output,options=options)
        
    def xxx_save_landscape(self,dest_path):
        with open(dest_path, 'w+') as container_file:
            container_file.write(self.container_template_landscape)

    def xxx_save_portrait(self,dest_path):
        with open(dest_path, 'w+') as container_file:
            container_file.write(self.container_template_portrait)
    def xxx_add_landscape_template(self,template):
        self.container_template_landscape=self.container_template_landscape+template.encode("utf-8")
        
    def xxx_add_portrait_template(self,template):       
        self.container_template_portrait=self.container_template_portrait+template.encode("utf-8")
    