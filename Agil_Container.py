# -*- coding: utf-8 -*-
import pdfkit
from bs4 import BeautifulSoup as soup
from Agil_Template import Template
import copy
import sys
sys.setrecursionlimit(10000)

class Container_doc(object):
    
    def __init__(self,template,content,sequence,doc_type):
        self.content=""
        if template: 
            template.__class__= Template
            content = template.content_html
            
        content_pages = content.find_all(attrs={'class':'Page_container'})
        if(content_pages):
            if not content_pages[0].has_attr('format'):
                for page in content_pages:
                    page['format'] = doc_type
            self.content = content_pages
            self.doc_type = doc_type
            self.sequence = sequence
    
class Container(object):
    
    def __init__(self,file_name=None):
        self.col_docs = {}
        self.sequence = 0 
        self.file_name = file_name
    
    def add(self,template):
        template.__class__= Template
        new_doc = Container_doc(copy.copy(template),None,self.sequence,template.get_format())
        self.sequence = self.sequence + 1
        self.col_docs[self.sequence] = new_doc
    
    def add_content(self,content,bookmark):
        page_container = content.find_all(attrs={"class":"Page_container"})[0]
        page_container["id"]=bookmark
        
        report = content.find(id="Report")
        if report:
            doc_type = report.get('format','Portrait')
            print 'add_content ---->',doc_type
        new_doc = Container_doc(None,
                                copy.copy(content),
                                self.sequence,
                                doc_type)
        self.sequence = self.sequence + 1
        self.col_docs[self.sequence] = new_doc
    
    
    def get_preview(self):    
        str_file = soup("""<!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8"  />
                    <script type="text/javascript" src="../inclu/jquery.js" ></script>
                    <script type="text/javascript" src="../inclu/etat_script.js" ></script>
                </head>
                <body id="viewer">
                    <!-- Debut de Rapport -->
                    <div id="Report">
                        
                    </div>
                    <!-- Fin de Rapport -->
                </body>
            </html>
            """)
        
        for seq,doc in self.col_docs.iteritems():
            for content_element in doc.content:
                str_file.find(id='Report').append(content_element)
                str_file.find(id='Report').append(str_file.new_tag("br"))
    
        return str_file.prettify()
    
    def save(self):
        str_file = self.get_preview()
        if str_file:     
            if self.file_name != None: 
                with open(self.file_name, 'w+') as container_file:
                    container_file.write(str_file)
        return self.file_name
    
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
        
