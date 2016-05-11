# coding=utf-8
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from django.shortcuts import render
from openpyxl import load_workbook, Workbook
import networkx as nx
from django.shortcuts import render_to_response
from django.template import RequestContext
from .models import NetworkElement, FiberRelationship, ConvergeNE
from . import forms
from functools import reduce


def upload_file(request):
    if request.method == 'POST':
        form = forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_excel(request.FILES['file'])
            return render(request, 'success.html')
    else:
        form = forms.UploadFileForm()
    return render_to_response('upload.html', {'form': form}, context_instance=RequestContext(request))


def handle_excel(request):
    # 创建一个Workbook对象以便将结果写入
    wb_write = Workbook(write_only=True)
    ws_write = wb_write.create_sheet()
    big_access_num_config = 8
    long_single_chain_num_config = 1
    big_converge_node_point_config = 80
    # 获取全地区环名集合
    ring_name_set = NetworkElement.objects.values_list('ring_name', flat=True).order_by('ring_name').distinct()
    # ---------------------------------------------------
    # ws_write.append(list(ring_name_set))
    # wb_write.save('1.xlsx')
    # return render_to_response('success.html')
    # ---------------------------------------------------

    # 所有接入环接入网元数
    total_access_ne_num = NetworkElement.objects.count()
    # print (total_access_ne_num)
    total_ring_access_ne_num = []
    # 所有单归网元表
    total_single_ne_num = []
    # print(total_access_ne_num)
    # # 所有成环网元列表
    # total_ne_ring = []
    # total_ne_single_re = []
    # 遍历ring_name_set，到NetworkElement和ConvergeNE两张表中搜索ring_name_set[]得到某一环下所有网元
    for rns in ring_name_set:
        ws_write.append(['环名称------------------------------'])
        ws_write.append(list(rns))
        # 获取某环接入环接入网元列表
        access_ne_list = list(NetworkElement.objects.filter(ring_name=rns).values_list('ne_name', flat=True))
        # 获取某环接入环汇聚网元列表
        converge_ne_list = list(ConvergeNE.objects.filter(ring_name=rns).values_list('cne_name', flat=True))
        # 获取某环接入环全部网元列表
        ne_list = access_ne_list + converge_ne_list
    #     # ---------------------------------------------------
    #     ws_write.append(access_ne_list)
    #     ws_write.append(converge_ne_list)
    # wb_write.save('2.xlsx')
    # return render_to_response('success.html')
    # # ---------------------------------------------------
        # 获取源跟宿均在该环全部网元列表中的纤缆连接关系列表
        fiber_relationship_list = FiberRelationship.objects.filter(source__in=ne_list).filter(target__in=ne_list)\
            .values_list('source', 'target')
    #     # ---------------------------------------------------
    #     for frl in fiber_relationship_list:
    #         ws_write.append(list(frl))
    # wb_write.save('3.xlsx')
    # return render_to_response('success.html')
    # # ---------------------------------------------------
        # 实例化一个空图
        g = nx.Graph()
        #
        path_list = []
    #     path_set = []
    #     not_path_set = []
    #     single_path = []
    #     single_re_path_set = []
        # 将路径列表加入到图中
        g.add_edges_from(fiber_relationship_list)

        # 找出接入环中任意两个汇聚网元之间的所有路径
        for a in range(0, len(converge_ne_list)-1):
            for b in range(a+1, len(converge_ne_list)):
                source_ne = converge_ne_list[a]
                target_ne = converge_ne_list[b]
                # ws_write.append(list(source_ne)+list(target_ne))
                for pth in nx.all_simple_paths(g, source=source_ne, target=target_ne):
                    if (len(pth)-2) > big_access_num_config:
                        ws_write.append(['超大接入环：'])
                        ws_write.append([len(pth)-2])
                        ws_write.append(pth)
                path_list.append(list(set(reduce(lambda x, y: x+y,
                                                 list(nx.all_simple_paths(g, source=source_ne, target=target_ne))))))
        # 获取每一个环成环网元列表
        ring_ne_list = list(set(reduce(lambda x, y: x+y, path_list)))
        # 获取每一个环未成环网元列表
        no_ring_ne_list = list(set(ne_list)-set(ring_ne_list))
        no_ring_ne_path = []

        for nrnl in no_ring_ne_list:
            for cnl in converge_ne_list:
                if nx.all_simple_paths(g, source=nrnl, target=cnl):
                    for nrnp in nx.all_simple_paths(g, source=nrnl, target=cnl):
                        if len(nrnp) > long_single_chain_num_config and len(set(nrnp) & set(ring_ne_list)) == 1:
                            ws_write.append(['汇聚长单链：'])
                            ws_write.append([len(nrnp)])
                            ws_write.append(nrnp)
                    # 未成环网元单归路径表
                    no_ring_ne_path.append(list(set(reduce(lambda x, y: x + y,
                                                           list(nx.all_simple_paths(g, source=nrnl, target=cnl))))))
        # 未成环网元单归网元表
        no_ring_ne_path_list = list(set(reduce(lambda x, y: x + y, no_ring_ne_path)))
        total_single_ne_num.append(len(no_ring_ne_path_list))
        # 接入网元成环列表
        ring_access_ne_list = []
        for c in range(0, len(ring_ne_list)):
            if ring_ne_list[c] not in converge_ne_list:
                ring_access_ne_list.append(ring_ne_list[c])
        ws_write.append(['--成环网元列表--'])
        ws_write.append(ring_access_ne_list)
        # print(len(ring_access_ne_list))
        total_ring_access_ne_num.append(len(ring_access_ne_list))
    # print (sum(total_ring_access_ne_num))
    ring_rate = float(sum(total_ring_access_ne_num))/float(total_access_ne_num)
    double_rate = 1-float(sum(total_single_ne_num))/float(total_access_ne_num)
    ws_write.append(['总成环率------------------------------'])
    ws_write.append(list(str(ring_rate)))
    ws_write.append(['总双归率------------------------------'])
    ws_write.append(list(str(double_rate)))
    # print (ring_rate)
    wb_write.save('6.xlsx')
    return render_to_response('success.html')
    #     # ---------------------------------------------------
    #     ws_write.append(ring_access_ne_list)
    # wb_write.save('5.xlsx')
    # return render_to_response('success.html')
    # # ---------------------------------------------------
    #             for ph in path_list:
    #                 ws_write.append(ph)
    # wb_write.save('4.xlsx')
    # return render_to_response('success.html')
    #     # 生成某一环成环网元列表
    #     for j in range(0, len(path_list)):
    #         for k in range(0, len(path_list[j])):
    #             if path_list[j][k] not in path_set:
    #                 path_set.append(path_list[j][k])
    #     # 生成某一环未成环网元列表
    #     for anl in access_ne_list:
    #         if anl not in path_set:
    #             not_path_set.append(anl)
    #     # 生成未成环网元到汇聚的所有路径并生成单归网元列表
    #     for a in range(0, len(not_path_set)):
    #         for b in range(0, len(converge_ne_list)):
    #             if nx.all_simple_paths(g, source=not_path_set[a], target=converge_ne_list[b]):
    #                 single_re_path = list(nx.all_simple_paths(g, source=not_path_set[a], target=converge_ne_list[b]))
    #                 for c in range(0, len(single_re_path)):
    #                     for d in range(0, len(single_re_path[c])):
    #                         if single_re_path[c][d] not in single_re_path_set:
    #                             single_re_path_set.append(single_re_path[c][d])
    #     total_ne_single_re.append(single_re_path_set)
    #
    #     # 将该环成环网元列表添加到所有成环网元列表
    #     total_ne_ring.append(path_set)
    #     ws_write.append(['-----------------------------------------------------------------------------'])
    # # 保存路径Excel
    # wb_write.save('path.xlsx')
    # # 全网成环率
    #
    # ring_rate = len(total_ne_ring) / total_ne
    # # ring = ConvergeNE.objects.all()
    # # for r in ring:
    # #     print (r.ring_name)
    #
    # return render_to_response('success.html', {'ring': ring_rate})
    # 读取纤缆连接关系表
    # wb_fiber = load_workbook(filename='./static/xianlan1.xlsx', read_only=True)
    # ws_fiber = wb_fiber.active

    # # 读取网元信息表
    # wb_ne = load_workbook(filename='./static/wangyuan.xlsx', read_only=True)
    # ws_ne = wb_ne.active
    #
    # # 读取汇聚网元信息表
    # wb_converge = load_workbook(filename='./static/convergeinfo_lite.xlsx', read_only=True)
    # ws_converge = wb_converge.active
    #
    # for k in range(2, ws_converge.max_row+1):
    #     print(k)
    #     cne_name = ws_converge.cell(row=k, column=2).value
    #     cne_type = 'hj'
    #     ring_name = ws_converge.cell(row=k, column=1).value
    #     ring_region = '宁波'
    #     cne = ConvergeNE(cne_name=cne_name, cne_type=cne_type, ring_name=ring_name, ring_region=ring_region)
    #     cne.save()

    #
    # # 定义将要添加进某一环图的路径列表
    # path_list = []
    #
    # # 定义接入环接入网元列表
    # access_ne = []
    #
    # # 定义接入环汇聚网元列表
    # converge_ne = []
    #
    # # 定义接入环列表
    # access_ring_list = []

    # 获取接入环列表
    # print ('正在导入接入网元表')
    # for i in range(2, ws_ne.max_row + 1):
    #     print (i)
    #     ne_name = ws_ne.cell(row=i, column=1).value
    #     ne_type = ws_ne.cell(row=i, column=2).value
    #     ne_ring = ws_ne.cell(row=i, column=3).value
    #     if ne_type in ('OptiX PTN 910', 'OptiX PTN 950', 'OptiX PTN 960'):
    #         # access_ring_list.append(ne_ring)
    #         ne = NetworkElement(ne_name=ne_name, ne_type=ne_type, ring_name=ne_ring, ring_region='宁波')
    #         ne.save()
    # print ('正在导入线缆关系表')
    # for j in range(2, ws_fiber.max_row + 1):
    #     print (j)
    #     source = ws_fiber.cell(row=j, column=1).value
    #     target = ws_fiber.cell(row=j, column=2).value
    #     weight = ws_fiber.cell(row=j, column=3).value
    #     fiber = FiberRelationship(source=source, target=target, edge_weight=weight)
    #     fiber.save()
    #
    # return render_to_response('success.html')
    # print(len(access_ring_list))
    # 将接入环列表转换为集合，使其唯一
    # access_ring_set = set(access_ring_list)

    # print(len(access_ring_set))

    #
    # for i in range(0, len(access_ring_set)):
    #     access_ring_set[i]

    # return render_to_response('success.html', {'access_ring_list': len(access_ring_list), 'access_ring_set': len(access_ring_set)})

    # wb_write = Workbook(write_only=True)
    # ws_write = wb_write.create_sheet()
    # ws_write.append(access_ring_set)
    # wb_write.save('path.xlsx')

    # # 分别生成接入环接入、汇聚网元
    # for i in range(11, ws_ne.max_row+1):
    #     ne_name = ws_ne.cell(row=i, column=1).value
    #     ne_type = ws_ne.cell(row=i, column=2).value
    #     if ne_type in ('OptiX PTN 910', 'OptiX PTN 950', 'OptiX PTN 960'):
    #         access_ne.append(ne_name)
    #     else:
    #         converge_ne.append(ne_name)
    # print access_ne
    # print converge_ne

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
