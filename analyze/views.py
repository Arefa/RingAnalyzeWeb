# coding=utf-8
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from django.shortcuts import render
from openpyxl import load_workbook, Workbook
import networkx as nx
from networkx import NetworkXError
from django.shortcuts import render_to_response
from django.template import RequestContext
# from .models import NetworkElement, FiberRelationship, ConvergeNE, BAR, Result, ARR, ARP, LSC, DR, BCNE, ErrorMsg, \
#     DetailResult
from .models import NetworkElement, FiberRelationship, ConvergeNE, Result, DetailResult
from . import forms
from functools import reduce
import sys

reload(sys)
sys.setdefaultencoding('utf8')


# 函数功能：上传Excel文件
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
    big_access_num_config = 12
    long_single_chain_num_config = 3
    big_converge_node_point_config = 80
    # 获取全地区环名集合
    # ring_name_set = NetworkElement.objects.values_list('ring_name', flat=True).order_by('ring_name').distinct()
    ring_name_set = ConvergeNE.objects.values_list('ring_name', flat=True).order_by('ring_name').distinct()
    # ---------------------------------------------------
    # ws_write.append(list(ring_name_set))
    # wb_write.save('1.xlsx')
    # return render_to_response('success.html')
    # ---------------------------------------------------

    # 所有接入环接入网元数
    total_access_ne_num = []

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
        total_access_ne_num.append(len(access_ne_list))
        # 获取某环接入环全部网元列表
        ne_list = access_ne_list + converge_ne_list
        #     # ---------------------------------------------------
        #     ws_write.append(access_ne_list)
        #     ws_write.append(converge_ne_list)
        # wb_write.save('2.xlsx')
        # return render_to_response('success.html')
        # # ---------------------------------------------------
        # 接入网元成环列表
        ring_access_ne_list = []
        # 未成环接入网元单归网元表
        no_ring_access_ne_list = []
        # 获取源跟宿均在该环全部网元列表中的纤缆连接关系列表
        fiber_relationship_list = FiberRelationship.objects.filter(source__in=ne_list).filter(target__in=ne_list) \
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
        for a in range(0, len(converge_ne_list) - 1):
            for b in range(a + 1, len(converge_ne_list)):
                source_ne = converge_ne_list[a]
                target_ne = converge_ne_list[b]
                # ws_write.append(list(source_ne)+list(target_ne))
                try:
                    if nx.all_simple_paths(g, source=source_ne, target=target_ne):
                        paths = nx.all_simple_paths(g, source=source_ne, target=target_ne)
                        for pth in paths:
                            if (len(pth) - 2) > big_access_num_config:
                                ws_write.append(['超大接入环：'])
                                ws_write.append([len(pth) - 2])
                                ws_write.append(pth)
                            for c in range(0, len(pth)):
                                if pth[c] not in path_list:
                                    path_list.append(pth[c])
                                    # path_list.append(list(set(reduce(lambda x, y: x + y, list(paths)))))
                except NetworkXError as nxe:
                    print(nxe.message)
                    continue

        # 获取每一个环成环网元列表
        # ring_ne_list = list(set(reduce(lambda x, y: x+y, path_list)))
        ring_ne_list = path_list
        # 获取每一个环未成环网元列表
        no_ring_ne_list = list(set(ne_list) - set(ring_ne_list))
        no_ring_ne_path = []

        for nrnl in no_ring_ne_list:
            for cnl in converge_ne_list:
                try:
                    if nx.all_simple_paths(g, source=nrnl, target=cnl):
                        for nrnp in nx.all_simple_paths(g, source=nrnl, target=cnl):
                            if len(nrnp) > long_single_chain_num_config and len(set(nrnp) & set(ring_ne_list)) == 1:
                                ws_write.append(['汇聚长单链：'])
                                ws_write.append([len(nrnp)])
                                ws_write.append(nrnp)
                                # 未成环网元单归路径表
                                no_ring_ne_path.append(list(set(reduce(lambda x, y: x + y,
                                                                       list(nx.all_simple_paths(g, source=nrnl,
                                                                                                target=cnl))))))
                except NetworkXError as nxe:
                    print(nxe.message)
                    continue
        # 未成环网元单归网元表
        if no_ring_ne_path:
            no_ring_ne_path_list = list(set(reduce(lambda x, y: x + y, no_ring_ne_path)))
            for nrnpl in no_ring_ne_path_list:
                if nrnpl not in converge_ne_list:
                    no_ring_access_ne_list.append(nrnpl)
        print(no_ring_access_ne_list)
        total_single_ne_num.append(len(no_ring_access_ne_list))

        for c in range(0, len(ring_ne_list)):
            if ring_ne_list[c] not in converge_ne_list:
                ring_access_ne_list.append(ring_ne_list[c])
        for nrnl in no_ring_ne_list:
            for ranl in ring_access_ne_list:
                try:
                    if nx.all_simple_paths(g, source=nrnl, target=ranl):
                        for nrnp in nx.all_simple_paths(g, source=nrnl, target=ranl):
                            if len(nrnp) > long_single_chain_num_config and len(set(nrnp) & set(ring_ne_list)) == 1:
                                ws_write.append(['普通长单链：'])
                                ws_write.append([len(nrnp)])
                                ws_write.append(nrnp)
                except NetworkXError as nxe:
                    print(nxe.message)
                    ErrorMsg.objects.get_or_create(ring_name=rns, msg=nxe.message)
                    continue
        ws_write.append(['--成环网元列表--'])
        ws_write.append(ring_access_ne_list)

        ws_write.append(['--成环率--'])
        single_ring_rate = float(len(ring_access_ne_list)) / float(len(access_ne_list))
        ws_write.append(list(str(single_ring_rate)))
        ws_write.append(['--双归率--'])
        single_double_rate = 1 - float(len(no_ring_access_ne_list)) / float(len(access_ne_list))
        ws_write.append(list(str(single_double_rate)))

        # print(len(ring_access_ne_list))
        total_ring_access_ne_num.append(len(ring_access_ne_list))
    print(sum(total_ring_access_ne_num))
    ring_rate = float(sum(total_ring_access_ne_num)) / float(sum(total_access_ne_num))
    double_rate = 1 - float(sum(total_single_ne_num)) / float(sum(total_access_ne_num))
    ws_write.append(['总成环率------------------------------'])
    ws_write.append(list(str(ring_rate)))
    ws_write.append(['总双归率------------------------------'])
    ws_write.append(list(str(double_rate)))
    print(ring_rate)
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
    # wb_fiber = load_workbook(filename='./static/xianlan.xlsx', read_only=True)
    # ws_fiber = wb_fiber.active
    #
    # # 读取网元信息表
    # wb_ne = load_workbook(filename='./static/wangyuan.xlsx', read_only=True)
    # ws_ne = wb_ne.active
    #
    # # 读取汇聚网元信息表
    # wb_converge = load_workbook(filename='./static/xiangshan.xlsx', read_only=True)
    # ws_converge = wb_converge.active
    # #
    # for k in range(1, ws_converge.max_row+1):
    #     print(k)
    #     cne_name = ws_converge.cell(row=k, column=1).value
    #     cne_type = 'hj'
    #     ring_name = ws_converge.cell(row=k, column=2).value
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

    # # 获取接入环列表
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
    # #
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


# 晓鸣需求
def produce_ring_fiber(request):
    ring_set = ConvergeNE.objects.values_list('ring_name', flat=True).order_by('ring_name').distinct()
    wb_write = Workbook(write_only=True)
    ws_write = wb_write.create_sheet()
    for rns in ring_set:
        ws_write.append(list(rns))
        ws_write.append(['----------------'])
        # 获取某环接入环接入网元列表
        access_ne_list = list(NetworkElement.objects.filter(ring_name=rns).values_list('ne_name', flat=True))
        # 获取某环接入环汇聚网元列表
        converge_ne_list = list(ConvergeNE.objects.filter(ring_name=rns).values_list('cne_name', flat=True))
        # 获取某环接入环全部网元列表
        ne_list = access_ne_list + converge_ne_list
        # 获取源跟宿均在该环全部网元列表中的纤缆连接关系列表
        fiber_relationship_list = FiberRelationship.objects.filter(source__in=ne_list).filter(target__in=ne_list) \
            .values_list('source', 'target')
        for t in range(0, len(fiber_relationship_list)):
            ws_write.append(fiber_relationship_list[t])
    wb_write.save('7.xlsx')
    return render_to_response('success.html')


# 函数功能：导入Excel数据到数据库中
# 要求：网元信息和纤缆连接关系的Excel表直接从网管上导出，转换为xlsx格式，其他无需改变
#       汇聚网元信息表为自有维护
def import_xlsx_data(request):
    # 读取网元信息表
    wb_neinfo = load_workbook(filename='./static/neinfo.xlsx', read_only=True)
    ws_neinfo = wb_neinfo.active
    # 读取汇聚网元信息表
    wb_cneinfo = load_workbook(filename='./static/cneinfo.xlsx', read_only=True)
    ws_cneinfo = wb_cneinfo.active
    # 读取纤缆连接关系表
    wb_ne2ne = load_workbook(filename='./static/ne2ne.xlsx', read_only=True)
    ws_ne2ne = wb_ne2ne.active
    # --------------------------------------------------------------------------
    # # 导入网元信息表中的普通网元到数据库
    # if ws_neinfo.cell(row=8, column=1).value == u'网元名称' and ws_neinfo.cell(row=8, column=2).value == u'网元类型' and ws_neinfo.cell(row=8, column=10).value == u'所属子网':
    #     # 定义接入网元类型
    #     access_ne_type = ('OptiX PTN 910', 'OptiX PTN 950', 'OptiX PTN 960', 'OptiX PTN 1900')
    #     for a_row in range(9, ws_neinfo.max_row + 1):
    #         ne_name = ws_neinfo.cell(row=a_row, column=1).value
    #         ne_type = ws_neinfo.cell(row=a_row, column=2).value
    #         ne_ring = ws_neinfo.cell(row=a_row, column=10).value
    #         region_list = ws_neinfo.cell(row=a_row, column=10).value
    #         ring_region = region_list[0:2]
    #         if ne_type in access_ne_type:
    #             print (u'正在导入第'+str(a_row)+u'条接入网元数据')
    #             NetworkElement.objects.create(ne_name=ne_name, ne_type=ne_type, ring_name=ne_ring, ring_region=ring_region)
    # else:
    #     print(u'网元信息表读取有误！')
    # # 导入汇聚网元信息表到数据库
    # if ws_cneinfo.cell(row=1, column=2).value == u'网元名称' and ws_cneinfo.cell(row=1, column=3).value == u'所属子网':
    #     for b_row in range(2, ws_cneinfo.max_row + 1):
    #         cne_name = ws_cneinfo.cell(row=b_row, column=2).value
    #         cne_type = 'OptiX PTN 390000'
    #         ring_name = ws_cneinfo.cell(row=b_row, column=3).value
    #         ring_region = ws_cneinfo.cell(row=b_row, column=1).value
    #         print(u'正在导入第' + str(b_row) + u'条汇聚网元数据')
    #         ConvergeNE.objects.create(cne_name=cne_name, cne_type=cne_type, ring_name=ring_name,
    #                                   ring_region=ring_region)
    # else:
    #     print(u'汇聚网元信息表读取有误！')
    # 导入纤缆连接关系表到数据库
    if ws_ne2ne.cell(row=8, column=6).value == u'源网元' and ws_ne2ne.cell(row=8, column=8).value == u'宿网元' and ws_ne2ne.cell(row=8, column=17).value == u'备注':
        for c_row in range(9, ws_ne2ne.max_row + 1):
            source = ws_ne2ne.cell(row=c_row, column=6).value
            target = ws_ne2ne.cell(row=c_row, column=8).value
            weight = ws_ne2ne.cell(row=c_row, column=17).value
            print(u'正在导入第' + str(c_row) + u'条纤缆连接关系数据')
            if weight == '1':
                weight_new = 1
                FiberRelationship.objects.create(source=source, target=target, edge_weight=weight_new)
            elif weight != '1' and weight != '0':
                weight_new = 1000
                FiberRelationship.objects.create(source=source, target=target, edge_weight=weight_new)

    else:
        print(u'纤缆连接关系表读取有误！')
    # --------------------------------------------------------------------------
    return render_to_response('success.html')


def main_handle(request):
    # 以下为计算参数配置-----------------------------
    # 超大接入环接入网元阈值
    big_access_num_config = 12
    # 长单链网元阈值
    long_single_chain_num_config = 4
    # 超大汇聚节点阈值
    big_converge_node_point_config = 0
    # 以上为计算参数配置-----------------------------

    # 在汇聚网元表中筛选出所有环名称
    ring_name_set = ConvergeNE.objects.values_list('ring_name', flat=True).order_by('ring_name').distinct()
    # 所有接入环接入网元数
    total_access_ne_num = []
    # 所有接入环成环接入网元数
    total_ring_access_ne_num = []
    # # 所有单归网元表
    # total_single_ne_num = []
    # 所有双归网元表
    total_double_ne_num = []
    # 遍历ring_name_set，到NetworkElement和ConvergeNE两张表中搜索ring_name_set[]得到某一环下所有网元
    for rns in ring_name_set:
        # 获取某环接入环接入网元列表
        access_ne_list = list(NetworkElement.objects.filter(ring_name=rns).values_list('ne_name', flat=True))
        # 获取某环接入环汇聚网元列表
        converge_ne_list = list(ConvergeNE.objects.filter(ring_name=rns).values_list('cne_name', flat=True))
        # 将该环接入网元数量添加至总数量列表
        total_access_ne_num.append(len(access_ne_list))
        # 获取某环接入环全部网元列表
        ne_list = access_ne_list + converge_ne_list
        # 接入网元成环列表
        ring_access_ne_list = []
        # # 未成环接入网元单归网元表
        # no_ring_access_ne_list = []
        # 获取源跟宿均在该环全部网元列表中的纤缆连接关系列表
        fiber_relationship_list = FiberRelationship.objects.filter(source__in=ne_list).filter(target__in=ne_list)\
            .values_list('source', 'target')
        # 实例化一个空图
        g = nx.Graph()
        # 定义用来存放成环网元的列表
        path_list = []
        # 将路径列表加入到图中
        g.add_edges_from(fiber_relationship_list)

        # 成环汇聚网元
        ring_cne = []
        # --------------------计算成环率和超大接入环-------------------
        # 找出接入环中任意两个汇聚网元之间的所有路径
        for a in range(0, len(converge_ne_list)-1):
            for b in range(a+1, len(converge_ne_list)):
                source_ne = converge_ne_list[a]
                target_ne = converge_ne_list[b]
                try:
                    # 判断路径非空
                    if nx.all_simple_paths(g, source=source_ne, target=target_ne):
                        if source_ne not in ring_cne:
                            ring_cne.append(source_ne)
                        elif target_ne not in ring_cne:
                            ring_cne.append(target_ne)
                        paths = nx.all_simple_paths(g, source=source_ne, target=target_ne)
                        for pth in paths:
                            # 去除路径中包含汇聚的情况
                            if len(set(pth) & set(converge_ne_list)) == 2:
                                if len(pth) > 2:
                                    pth_str = '->'.join(pth)
                                    DetailResult.objects.create(ring_name=rns, arp=pth_str)
                                    # ARP.objects.get_or_create(ring_name=rns, arp=pth_str)
                                    # 判断超大接入环并写入数据库BAR数据表中
                                    if (len(pth) - 2) >= big_access_num_config:
                                        DetailResult.objects.create(ring_name=rns, ne_num=len(pth)-2, bar_ne=pth_str)
                                        # BAR.objects.get_or_create(ring_name=rns, ne_num=len(pth)-2, bar_ne=pth_str)
                                    # 将该路径中的网元加入到该环成环网元列表中，剔除首尾的汇聚网元
                                    for c in range(1, len(pth)-1):
                                        if pth[c] not in path_list:
                                            path_list.append(pth[c])
                except NetworkXError as nxe:
                    print (nxe.message)
                    DetailResult.objects.get_or_create(ring_name=rns, msg=nxe.message)
                    continue
        # 获取每一个环成环网元列表
        ring_ne_list = path_list
        ring_str = '->'.join(ring_ne_list)
        # 将该环的成环率写入数据库ARR数据表中
        try:
            DetailResult.objects.create(ring_name=rns, arr=float(len(ring_ne_list)) / float(len(access_ne_list)),
                                      arr_ne=ring_str)
            # ARR.objects.get_or_create(ring_name=rns, arr=float(len(ring_ne_list)) / float(len(access_ne_list)),
            #                          arr_ne=ring_str)
        except ZeroDivisionError:
            print('ZeroDivisionError')
            DetailResult.objects.get_or_create(ring_name=rns, msg='ZeroDivisionError')
            # ErrorMsg.objects.get_or_create(ring_name=rns, msg=nxe.message)
            continue
        # 将该环成环网元的数量添加到总列表中
        total_ring_access_ne_num.append(len(ring_ne_list))
        # 获取每一个环未成环网元列表
        no_ring_ne_list = list(set(access_ne_list)-set(ring_ne_list))

        # --------------------计算长单链-------------------
        # 计算长单链
        for rnl in ring_ne_list:
            for nrnl in no_ring_ne_list:
                try:
                    if nx.all_simple_paths(g, source=rnl, target=nrnl):
                        for nrnp in nx.all_simple_paths(g, source=rnl, target=nrnl):
                            if len(set(nrnp) & set(ring_ne_list + converge_ne_list)) == 1 and len(nrnp) >= long_single_chain_num_config:
                                nrnp_str = '->'.join(nrnp)
                                DetailResult.objects.create(ring_name=rns, lsc_num=len(nrnp), lsc_ne=nrnp_str)
                                # LSC.objects.get_or_create(ring_name=rns, lsc_num=len(nrnp), lsc_ne=nrnp)
                except NetworkXError as nxe:
                    print(nxe.message)
                    DetailResult.objects.get_or_create(ring_name=rns, msg=nxe.message)
                    # ErrorMsg.objects.get_or_create(ring_name=rns, msg=nxe.message)
                    continue
        # 处理重复的长单链
        # lsc_original=LSC.objects.filter(ring_name=rns).values_list('lsc_num', 'lsc_ne').order_by('-lsc_num')
        # for i in range(0, len(lsc_original)-1):
        #     for j in range(i+1, len(lsc_original)):
        #         big = lsc_original[i]
        #         lessbig = lsc_original[j]
        #         if set(big[1]).issuperset(set(lessbig[1])):
        #             if LSC.objects.filter(ring_name=rns).filter(lsc_num=lessbig[0]).filter(lsc_ne=lessbig[1]):
        #                 LSC.objects.filter(ring_name=rns).filter(lsc_num=lessbig[0]).filter(lsc_ne=lessbig[1]).delete()
        # lsc_new = LSC.objects.filter(ring_name=rns).values_list('lsc_num', 'lsc_ne').order_by('-lsc_num')
        # for k in range(0, len(lsc_new)):
        #     DetailResult.objects.create(ring_name=rns, lsc_num=lsc_new[k][0], lsc_ne=lsc_new[k][1])
        # --------------------计算双归率-------------------
        # 定义单归网元列表
        single_accsess_ne = []
        # 计算单归
        for cnl in converge_ne_list:
            for nrnl in no_ring_ne_list:
                try:
                    if nx.all_simple_paths(g, source=cnl, target=nrnl):
                        for nrnp in nx.all_simple_paths(g, source=cnl, target=nrnl):
                            if len(set(nrnp) & set(ring_ne_list+converge_ne_list)) == 1:
                                for c in range(0, len(nrnp)):
                                    if nrnp[c] not in single_accsess_ne:
                                        single_accsess_ne.append(nrnp[c])
                except NetworkXError as nxe:
                    print (nxe.message)
                    DetailResult.objects.get_or_create(ring_name=rns, msg=nxe.message)
                    continue
        double_accsess_ne = list(set(access_ne_list)-(set(single_accsess_ne)-set(converge_ne_list)))
        # 将该环双归率写入数据库DR数据表中
        DetailResult.objects.create(ring_name=rns, dr=float(len(double_accsess_ne))/float(len(access_ne_list)))
        # DR.objects.get_or_create(ring_name=rns, dr=float(len(double_accsess_ne))/float(len(access_ne_list)))
        total_double_ne_num.append(len(double_accsess_ne))

        # --------------------计算超大汇聚节点-------------------
        # set(access_ne_list)-set()
        # len(ring_cne)
        #

        for a in range(0, len(converge_ne_list)):
            single_single_ne = []
            for b in range(0, len(no_ring_ne_list)):
                try:
                    if nx.all_simple_paths(g, source=converge_ne_list[a], target=no_ring_ne_list[b]):
                        for ph in nx.all_simple_paths(g, source=converge_ne_list[a], target=no_ring_ne_list[b]):
                            if len(set(ph) & set(ring_ne_list + converge_ne_list)) == 1:
                                for p in range(1, len(ph)):
                                    if ph[p] not in single_single_ne:
                                        single_single_ne.append(ph[p])
                except NetworkXError as nxe:
                    print(nxe.message)
                    DetailResult.objects.get_or_create(ring_name=rns, msg=nxe.message)
                    # ErrorMsg.objects.get_or_create(ring_name=rns, msg=nxe.message)
                    continue
            point = len(single_single_ne) + float(len(double_accsess_ne))/float(len(converge_ne_list))
            if point >= big_converge_node_point_config:
                DetailResult.objects.create(ring_name=rns, cne_point=point, bcne_cne=converge_ne_list[a])
                # BCNE.objects.get_or_create(ring_name=rns, cne_point=point, bcne_cne=converge_ne_list[a])

    ring_rate = float(sum(total_ring_access_ne_num))/float(sum(total_access_ne_num))
    double_rate = float(sum(total_double_ne_num))/float(sum(total_access_ne_num))
    Result.objects.get_or_create(total_arr=ring_rate, total_dr=double_rate)

    # [(id, u''),(id, u''),....]
    arplist = DetailResult.objects.values_list('id', 'arp')
    for al in arplist:
        weightlist = []
        allist = str(al[1]).split('->')
        for x in range(0, len(allist) - 1):
            if FiberRelationship.objects.filter(source=allist[x]).filter(target=allist[x + 1]):
                v = FiberRelationship.objects.filter(source=allist[x]).filter(target=allist[x + 1]).values_list(
                    'edge_weight', flat=True)
                weightlist.append(v)
            elif FiberRelationship.objects.filter(source=allist[x + 1]).filter(target=allist[x]):
                v = FiberRelationship.objects.filter(source=allist[x + 1]).filter(target=allist[x]).values_list(
                    'edge_weight', flat=True)
                weightlist.append(v)
        print(weightlist)

    # list = []
    # teststr = "51-11-象山昌国->51-180-TXS昌国基站->51-92-中国渔村->53-99-XS阳光雅苑B区SF->53-221-XS阳光雅苑->51-67-杉树岙->52-135-TXS东门岛->51-66-东门->52-95-宁波市象山县石浦镇XWJBD->51-65-小网巾->52-71-TXS鹤翔->52-104-TXS后塘角->51-12-象山后塘角"
    # testlist = str(teststr).split('->')
    # for test in range(0,len(testlist)-1):
    #     if FiberRelationship.objects.filter(source=testlist[test]).filter(target=testlist[test + 1]):
    #         v = FiberRelationship.objects.filter(source=testlist[test]).filter(target=testlist[test + 1]).values_list('edge_weight', flat=True)
    #         list.append(v)
    #     elif FiberRelationship.objects.filter(source=testlist[test + 1]).filter(target=testlist[test]):
    #         v = FiberRelationship.objects.filter(source=testlist[test + 1]).filter(target=testlist[test]).values_list('edge_weight', flat=True)
    #         list.append(v)
    # print(list)

        if len(weightlist) > 0 and DetailResult.objects.filter(id=al[0]):
            if str(weightlist[0]) == "[u'1000']" and DetailResult.objects.filter(id=al[0]):
                for wln in range(1, len(weightlist)):
                    if str(weightlist[wln]) != str(weightlist[0]) and wln < len(weightlist)-1 and DetailResult.objects.filter(id=al[0]):
                        for wlnl in range(wln+1, len(weightlist)):
                            if str(weightlist[wlnl]) == str(weightlist[0]) and DetailResult.objects.filter(id=al[0]):
                                DetailResult.objects.filter(id=al[0]).delete()
            elif str(weightlist[0]) == "[u'1']" and DetailResult.objects.filter(id=al[0]):
                for wln in range(1, len(weightlist)):
                    if str(weightlist[wln]) != str(weightlist[0]) and wln < len(weightlist)-1 and DetailResult.objects.filter(id=al[0]):
                        for wln1 in range(wln+1, len(weightlist)):
                            if str(weightlist[wln1]) != str(weightlist[wln]) and wln1 < len(weightlist)-1 and DetailResult.objects.filter(id=al[0]):
                                for wln2 in range(wln1+1, len(weightlist)):
                                    if str(weightlist[wln2]) != str(weightlist[wln1]) and DetailResult.objects.filter(id=al[0]):
                                        DetailResult.objects.filter(id=al[0]).delete()




    # print(weightlist)
    # print (weightlist)
    # if len(weightlist)==0:
    #     print (weightlist)
    return render_to_response('success.html')
