# Author: Alex Ksikes 

import web
import mimetypes

class public:
    def GET(self): 
        public_dir = 'public'
        try:
            file_name = web.ctx.path.split('/')[-1]
            web.header('Content-type', mime_type(file_name))
            return open(public_dir + web.ctx.path, 'rb').read()
        except IOError:
            raise web.notfound()

# class mediaUploaded:
#     def GET(self): 
#         mediaUploaded_dir = 'upload'
#         try:
#             file_name = web.ctx.path.split('/')[-1]
#             web.header('Content-type', mime_type(file_name))
#             return open(mediaUploaded_dir + web.ctx.path, 'rb').read()
#         except IOError:
#             raise web.notfound()

# class imageUploaded:
#     def GET(self): 
#         imageUploaded_dir = 'static'
#         try:
#             file_name = web.ctx.path.split('/')[-1]
#             web.header('Content-type', mime_type(file_name))
#             return open(imageUploaded_dir + web.ctx.path, 'rb').read()
#         except IOError:
#             raise web.notfound()
            
def mime_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream' 
