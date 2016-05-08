# coding=utf-8
from django.shortcuts import render
# from openpyxl import load_workbook, Workbook
# import networkx as nx
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from . import forms


def upload_file(request):
    if request.method == 'POST':
        form = forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_excel(request.FILES['file'])
            return HttpResponseRedirect('/success')
    else:
        form = forms.UploadFileForm()
    return render_to_response('upload.html', {'form': form})


def handle_excel(request):
    return render(request)


def upload_success(request):
    pass

# # 读取纤缆连接关系表
# wb_fiber = load_workbook(filename='testbeilun.xlsx', read_only=True)
# ws_fiber = wb_fiber.active
#
# # 定义将要添加进某一环图的路径列表
# path_list = []
#
# # 读取某一环的网元表
# wb_ne = load_workbook(filename='beilun01.xlsx', read_only=True)
# ws_ne = wb_ne.active
#
# # 定义接入环接入网元列表
# access_ne = []
#
# # 定义接入环汇聚网元列表
# converge_ne = []
#
# # 分别生成接入环接入、汇聚网元
# for i in range(11, ws_ne.max_row+1):
#     ne_name = ws_ne.cell(row=i, column=1).value
#     ne_type = ws_ne.cell(row=i, column=2).value
#     if ne_type in ('OptiX PTN 910', 'OptiX PTN 950', 'OptiX PTN 960'):
#         access_ne.append(ne_name)
#     else:
#         converge_ne.append(ne_name)
#
# # 定义接入环所有网元列表
# total_ne = access_ne + converge_ne
# # print total_ne
#
# # 搜索线缆连接关系表，找出源宿都在total_ne中的路径
# for i in range(11, ws_fiber.max_row+1):
#     source_node = ws_fiber.cell(row=i, column=6).value
#     target_node = ws_fiber.cell(row=i, column=8).value
#     if source_node in total_ne and target_node in total_ne:
#         node_path = (source_node, target_node)
#         path_list.append(node_path)
#
# # 实例化一个空图
# G = nx.Graph()
#
# # 将路径列表加入到图中
# G.add_edges_from(path_list)
#
# # 创建一个Workbook对象以便将结果写入
# wb_write = Workbook(write_only=True)
# ws_write = wb_write.create_sheet()
#
# # 找出接入环中任意两个汇聚网元之间的所有路径
# for i in range(0, len(converge_ne)-1):
#     for j in range(i+1, len(converge_ne)):
#         source_ne = converge_ne[i]
#         target_ne = converge_ne[j]
#         ws_write.append(list(source_ne)+list(target_ne))
#         for path in nx.all_simple_paths(G, source=source_ne, target=target_ne):
#             ws_write.append(list(path))
#
# # 保存路径Excel
# wb_write.save('path.xlsx')



