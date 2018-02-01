# coding:utf-8
# author:ChrisZZ
# description: 从caffemodel文件解析出网络训练信息，以类似train.prototxt的形式输出到屏幕

#import _init_paths
import caffe.proto.caffe_pb2 as caffe_pb2

caffemodel_filename = 'RA_CNN.caffemodel'
model = caffe_pb2.NetParameter()

f=open(caffemodel_filename, 'rb')
model.ParseFromString(f.read())
f.close()

layers = model.layer
print 'name: "%s"'%model.name
layer_id=-1
for layer in layers:
    layer_id = layer_id + 1
    print 'layer {'
    print '  name: "%s"'%layer.name
    print '  type: "%s"'%layer.type

    
    tops = layer.top
    for top in tops:
        print '  top: "%s"'%top
    
    bottoms = layer.bottom
    for bottom in bottoms:
        print '  bottom: "%s"'%bottom
    
    if len(layer.include)>0:
        print '  include {'
        includes = layer.include
        phase_mapper={
            '0': 'TRAIN',
            '1': 'TEST'
        }
        
        for include in includes:
            if include.phase is not None:
                print '    phase: ', phase_mapper[str(include.phase)]
        print '  }'
    
    if layer.transform_param is not None and layer.transform_param.scale is not None and layer.transform_param.scale!=1:
        print '  transform_param {'
        print '    scale: %s'%layer.transform_param.scale
        print '  }'

    if layer.data_param is not None and (layer.data_param.source!="" or layer.data_param.batch_size!=0 or layer.data_param.backend!=0):
        print '  data_param: {'
        if layer.data_param.source is not None:
            print '    source: "%s"'%layer.data_param.source
        if layer.data_param.batch_size is not None:
            print '    batch_size: %d'%layer.data_param.batch_size
        if layer.data_param.backend is not None:
            print '    backend: %s'%layer.data_param.backend
        print '  }'
        
    if layer.param is not None:
        params = layer.param
        for param in params:
            print '  param {'
            if param.lr_mult is not None:
                print '    lr_mult: %s'% param.lr_mult
            print '  }'
    
    if layer.convolution_param is not None:
        print '  convolution_param {'
        conv_param = layer.convolution_param
        if conv_param.num_output is not None:
            print '    num_output: %d'%conv_param.num_output
        if len(conv_param.kernel_size) > 0:
            for kernel_size in conv_param.kernel_size:
                print '    kernel_size: ',kernel_size
        if len(conv_param.stride) > 0:
            for stride in conv_param.stride:
                print '    stride: ', stride
        if conv_param.weight_filler is not None:
            print '    weight_filler {'
            print '      type: "%s"'%conv_param.weight_filler.type
            print '    }'
        if conv_param.bias_filler is not None:
            print '    bias_filler {'
            print '      type: "%s"'%conv_param.bias_filler.type
            print '    }'
        print '  }'
    
    print '}'
