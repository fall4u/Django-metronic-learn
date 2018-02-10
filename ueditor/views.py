# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import os
import random
import urllib

from django.conf import settings as gSettings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

TOOLBARS_SETTINGS={
    "besttome":[['source','undo', 'redo','bold', 'italic', 'underline','forecolor', 'backcolor','superscript','subscript',"justifyleft","justifycenter","justifyright","insertorderedlist","insertunorderedlist","blockquote",'formatmatch',"removeformat",'autotypeset','inserttable',"pasteplain","wordimage","searchreplace","map","preview","fullscreen"], ['insertcode','paragraph',"fontfamily","fontsize",'link', 'unlink','insertimage','insertvideo','attachment','emotion',"date","time"]],
    "mini":[['source','|','undo', 'redo', '|','bold', 'italic', 'underline','formatmatch','autotypeset', '|', 'forecolor', 'backcolor','|', 'link', 'unlink','|','simpleupload','attachment']],
    "normal":[['source','|','undo', 'redo', '|','bold', 'italic', 'underline','removeformat', 'formatmatch','autotypeset', '|', 'forecolor', 'backcolor','|', 'link', 'unlink','|','simpleupload', 'emotion','attachment', '|','inserttable', 'deletetable', 'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown', 'splittocells', 'splittorows', 'splittocols']]
}


#请参阅php文件夹里面的config.json进行配置
UEditorUploadSettings={
   #上传图片配置项
    "imageActionName": "uploadimage", #执行上传图片的action名称
    "imageMaxSize": 10485760, #上传大小限制，单位B,10M
    "imageFieldName": "upfile", #* 提交的图片表单名称 */
    "imageUrlPrefix":"",
    "imagePathFormat":"",
    "imageAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"], #上传图片格式显示

    #涂鸦图片上传配置项 */
    "scrawlActionName": "uploadscrawl", #执行上传涂鸦的action名称 */
    "scrawlFieldName": "upfile", #提交的图片表单名称 */
    "scrawlMaxSize": 10485760, #上传大小限制，单位B  10M
    "scrawlUrlPrefix":"",
    "scrawlPathFormat":"",

    #截图工具上传 */
    "snapscreenActionName": "uploadimage", #执行上传截图的action名称 */
    "snapscreenPathFormat":"",
    "snapscreenUrlPrefix":"",

    #抓取远程图片配置 */
    "catcherLocalDomain": ["127.0.0.1", "localhost", "img.baidu.com"],
    "catcherPathFormat":"",
    "catcherActionName": "catchimage", #执行抓取远程图片的action名称 */
    "catcherFieldName": "source", #提交的图片列表表单名称 */
    "catcherMaxSize": 10485760, #上传大小限制，单位B */
    "catcherAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"], #抓取图片格式显示 */
    "catcherUrlPrefix":"",
    #上传视频配置 */
    "videoActionName": "uploadvideo", #执行上传视频的action名称 */
    "videoPathFormat":"",
    "videoFieldName": "upfile", # 提交的视频表单名称 */
    "videoMaxSize": 102400000, #上传大小限制，单位B，默认100MB */
    "videoUrlPrefix":"",
    "videoAllowFiles": [
        ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
        ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid"], #上传视频格式显示 */

    #上传文件配置 */
    "fileActionName": "uploadfile", #controller里,执行上传视频的action名称 */
    "filePathFormat":"",
    "fileFieldName": "upfile",#提交的文件表单名称 */
    "fileMaxSize": 204800000, #上传大小限制，单位B，200MB */
    "fileUrlPrefix": "",#文件访问路径前缀 */
    "fileAllowFiles": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp",
        ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
        ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid",
        ".rar", ".zip", ".tar", ".gz", ".7z", ".bz2", ".cab", ".iso",
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt", ".md", ".xml"
    ], #上传文件格式显示 */

    #列出指定目录下的图片 */
    "imageManagerActionName": "listimage", #执行图片管理的action名称 */
    "imageManagerListPath":"",
    "imageManagerListSize": 30, #每次列出文件数量 */
    "imageManagerAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"], #列出的文件类型 */
    "imageManagerUrlPrefix": "",#图片访问路径前缀 */

    #列出指定目录下的文件 */
    "fileManagerActionName": "listfile", #执行文件管理的action名称 */
    "fileManagerListPath":"",
    "fileManagerUrlPrefix": "",
    "fileManagerListSize": 30, #每次列出文件数量 */
    "fileManagerAllowFiles": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp",".tif",".psd"
        ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
        ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid",
        ".rar", ".zip", ".tar", ".gz", ".7z", ".bz2", ".cab", ".iso",
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt", ".md", ".xml",
        ".exe",".com",".dll",".msi"
    ] #列出的文件类型 */
}

UEditorSettings={
    "toolbars":TOOLBARS_SETTINGS["normal"],
    "autoFloatEnabled":False,
    "defaultPathFormat":"upload/desc/%(basename)s_%(datetime)s_%(rnd)s.%(extname)s"   #默认保存上传文件的命名方式
}
def get_path_format_vars():
    return {
        "year":datetime.datetime.now().strftime("%Y"),
        "month":datetime.datetime.now().strftime("%m"),
        "day":datetime.datetime.now().strftime("%d"),
        "date": datetime.datetime.now().strftime("%Y%m%d"),
        "time":datetime.datetime.now().strftime("%H%M%S"),
        "datetime":datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "rnd":random.randrange(100,999)
    }


def get_output_path(request,path_format,path_format_var):
    #取得输出文件的路径
    OutputPathFormat=(request.GET.get(path_format, UEditorSettings["defaultPathFormat"]) % path_format_var).replace("\\","/")
    #分解OutputPathFormat
    OutputPath,OutputFile=os.path.split(OutputPathFormat)
    OutputPath=os.path.join(gSettings.MEDIA_ROOT,OutputPath)
    if not OutputFile:#如果OutputFile为空说明传入的OutputPathFormat没有包含文件名，因此需要用默认的文件名
        OutputFile=UEditorSettings["defaultPathFormat"] % path_format_var
        OutputPathFormat=os.path.join(OutputPathFormat,OutputFile)
    if not os.path.exists(OutputPath):
        os.makedirs(OutputPath)
    return ( OutputPathFormat,OutputPath,OutputFile)    


@csrf_exempt
def UploadFile(request):
    """上传文件"""
    if not request.method=="POST":
        return  HttpResponse(json.dumps(u"{'state:'ERROR'}"),content_type="application/javascript")

    state="SUCCESS"
    action=request.GET.get("action")
    #上传文件
    upload_field_name={
        "uploadfile":"fileFieldName",
        "uploadimage":"imageFieldName",
        "uploadscrawl":"scrawlFieldName",
        "catchimage":"catcherFieldName",
        "uploadvideo":"videoFieldName",
    }
    UploadFieldName=request.GET.get(upload_field_name[action],UEditorUploadSettings.get(action,"upfile"))

    #上传涂鸦，涂鸦是采用base64编码上传的，需要单独处理
    if action=="uploadscrawl":
        upload_file_name="scrawl.png"
        upload_file_size=0
    else:
        #取得上传的文件
        file=request.FILES.get(UploadFieldName,None)
        if file is None:return  HttpResponse(json.dumps(u"{'state:'ERROR'}") ,content_type="application/javascript")
        upload_file_name=file.name
        upload_file_size=file.size

    #取得上传的文件的原始名称
    upload_original_name,upload_original_ext=os.path.splitext(upload_file_name)

    #文件类型检验
    upload_allow_type={
        "uploadfile":"fileAllowFiles",
        "uploadimage":"imageAllowFiles",
        "uploadvideo":"videoAllowFiles"
    }
    if upload_allow_type.has_key(action):
        allow_type= list(request.GET.get(upload_allow_type[action],UEditorUploadSettings.get(upload_allow_type[action],"")))
        if not upload_original_ext.lower()  in allow_type:
            state=u"服务器不允许上传%s类型的文件。" % upload_original_ext

    #大小检验
    upload_max_size={
        "uploadfile":"filwMaxSize",
        "uploadimage":"imageMaxSize",
        "uploadscrawl":"scrawlMaxSize",
        "uploadvideo":"videoMaxSize"
    }
    max_size=long(request.GET.get(upload_max_size[action],UEditorUploadSettings.get(upload_max_size[action],0)))
    if  max_size!=0:
        from utils import FileSize
        MF=FileSize(max_size)
        if upload_file_size>MF.size:
            state=u"上传文件大小不允许超过%s。" % MF.FriendValue

    #检测保存路径是否存在,如果不存在则需要创建
    upload_path_format={
        "uploadfile":"filePathFormat",
        "uploadimage":"imagePathFormat",
        "uploadscrawl":"scrawlPathFormat",
        "uploadvideo":"videoPathFormat"
    }

    path_format_var=get_path_format_vars()
    path_format_var.update({
        "basename":upload_original_name,
        "extname":upload_original_ext[1:],
        "filename":upload_file_name,
    })
    #取得输出文件的路径
    OutputPathFormat,OutputPath,OutputFile=get_output_path(request,upload_path_format[action],path_format_var)

    #所有检测完成后写入文件
    if state=="SUCCESS":
        if action=="uploadscrawl":
            state=save_scrawl_file(request, os.path.join(OutputPath,OutputFile))
        else:
            #保存到文件中，如果保存错误，需要返回ERROR
            upload_module_name = UEditorUploadSettings.get("upload_module", None)
            if upload_module_name:
                mod = import_module(upload_module_name)
                state = mod.upload(file, OutputPathFormat)
            else:
                state = save_upload_file(file, os.path.join(OutputPath, OutputFile))

    #返回数据
    return_info = {
        'url': urllib.basejoin(gSettings.MEDIA_URL , OutputPathFormat) ,                # 保存后的文件名称
        'original': upload_file_name,                  #原始文件名
        'type': upload_original_ext,
        'state': state,                         #上传状态，成功时返回SUCCESS,其他任何值将原样返回至图片上传框中
        'size': upload_file_size
    }

    print return_info 

    return HttpResponse(json.dumps(return_info,ensure_ascii=False),content_type="application/javascript")



#保存上传的文件
def save_upload_file(PostFile,FilePath):
    try:
        f = open(FilePath, 'wb')
        for chunk in PostFile.chunks():
            f.write(chunk)
    except Exception,E:
        f.close()
        return u"写入文件错误:"+ E.message
    f.close()
    return u"SUCCESS"




@csrf_exempt
def get_ueditor_settings(request):
    return HttpResponse(json.dumps(UEditorUploadSettings,ensure_ascii=False), content_type="application/javascript")

@csrf_exempt
def get_ueditor_controller(request):
    """获取ueditor的后端URL地址    """

    action=request.GET.get("action","")
    reponseAction={
        "config":get_ueditor_settings,
        "uploadimage":UploadFile,
        # "uploadscrawl":UploadFile,
        # "uploadvideo":UploadFile,
        # "uploadfile":UploadFile,
        # "catchimage":catcher_remote_image,
        # "listimage":list_files,
        # "listfile":list_files
    }
    print " +++ get_ueditor_controller +++"
    return reponseAction[action](request)