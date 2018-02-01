#!/usr/bin/env python


"""
- ae(v): context-adaptive arithmetic entropy-coded syntax element. The parsing process for this descriptor is
         specified in clause 9.3.
- b(8):  byte having any pattern of bit string (8 bits). The parsing process
         for this descriptor is specified by the return value of the function
         read_bits( 8 ).
- f(n):  fixed-pattern bit string using n bits written (from left to right)
         with the left bit first. The parsing process for this descriptor is specified
         by the return value of the function read_bits( n ).
- se(v): signed integer 0-th order Exp-Golomb-coded syntax element with the left bit first. The parsing process
         for this descriptor is specified in clause 9.2.
- u(n):  unsigned integer using n bits. When n is "v" in the syntax table, the number of bits varies in a manner
         dependent on the value of other syntax elements. The parsing process for this descriptor is specified by the
         return value of the function read_bits( n ) interpreted as a binary representation of an unsigned integer with
         most significant bit written first.
- ue(v): unsigned integer 0-th order Exp-Golomb-coded syntax element with the left bit first. The parsing
         process for this descriptor is specified in clause 9.2.

"""

import sys
import os
import re
from bitstring import BitArray, BitStream


class NalUnitType:
    """
    Table 7-1 - NAL unit type codes and NAL unit type classes
    copypaste from source/Lib/TLibCommon/CommonDef.h
    """
    NAL_UNIT_CODED_SLICE_TRAIL_N = 0
    NAL_UNIT_CODED_SLICE_TRAIL_R = 1

    NAL_UNIT_CODED_SLICE_TSA_N = 2
    NAL_UNIT_CODED_SLICE_TSA_R = 3

    NAL_UNIT_CODED_SLICE_STSA_N = 4
    NAL_UNIT_CODED_SLICE_STSA_R = 5

    NAL_UNIT_CODED_SLICE_RADL_N = 6
    NAL_UNIT_CODED_SLICE_RADL_R = 7

    NAL_UNIT_CODED_SLICE_RASL_N = 8
    NAL_UNIT_CODED_SLICE_RASL_R = 9

    NAL_UNIT_RESERVED_VCL_N10 = 10
    NAL_UNIT_RESERVED_VCL_R11 = 11
    NAL_UNIT_RESERVED_VCL_N12 = 12
    NAL_UNIT_RESERVED_VCL_R13 = 13
    NAL_UNIT_RESERVED_VCL_N14 = 14
    NAL_UNIT_RESERVED_VCL_R15 = 15

    NAL_UNIT_CODED_SLICE_BLA_W_LP = 16
    NAL_UNIT_CODED_SLICE_BLA_W_RADL = 17
    NAL_UNIT_CODED_SLICE_BLA_N_LP = 18
    NAL_UNIT_CODED_SLICE_IDR_W_RADL = 19
    NAL_UNIT_CODED_SLICE_IDR_N_LP = 20
    NAL_UNIT_CODED_SLICE_CRA = 21
    NAL_UNIT_RESERVED_IRAP_VCL22 = 22
    NAL_UNIT_RESERVED_IRAP_VCL23 = 23

    NAL_UNIT_RESERVED_VCL24 = 24
    NAL_UNIT_RESERVED_VCL25 = 25
    NAL_UNIT_RESERVED_VCL26 = 26
    NAL_UNIT_RESERVED_VCL27 = 27
    NAL_UNIT_RESERVED_VCL28 = 28
    NAL_UNIT_RESERVED_VCL29 = 29
    NAL_UNIT_RESERVED_VCL30 = 30
    NAL_UNIT_RESERVED_VCL31 = 31

    NAL_UNIT_VPS = 32
    NAL_UNIT_SPS = 33
    NAL_UNIT_PPS = 34
    NAL_UNIT_ACCESS_UNIT_DELIMITER = 35
    NAL_UNIT_EOS = 36
    NAL_UNIT_EOB = 37
    NAL_UNIT_FILLER_DATA = 38
    NAL_UNIT_PREFIX_SEI = 39
    NAL_UNIT_SUFFIX_SEI = 40

    NAL_UNIT_RESERVED_NVCL41 = 41
    NAL_UNIT_RESERVED_NVCL42 = 42
    NAL_UNIT_RESERVED_NVCL43 = 43
    NAL_UNIT_RESERVED_NVCL44 = 44
    NAL_UNIT_RESERVED_NVCL45 = 45
    NAL_UNIT_RESERVED_NVCL46 = 46
    NAL_UNIT_RESERVED_NVCL47 = 47
    NAL_UNIT_UNSPECIFIED_48 = 48
    NAL_UNIT_UNSPECIFIED_49 = 49
    NAL_UNIT_UNSPECIFIED_50 = 50
    NAL_UNIT_UNSPECIFIED_51 = 51
    NAL_UNIT_UNSPECIFIED_52 = 52
    NAL_UNIT_UNSPECIFIED_53 = 53
    NAL_UNIT_UNSPECIFIED_54 = 54
    NAL_UNIT_UNSPECIFIED_55 = 55
    NAL_UNIT_UNSPECIFIED_56 = 56
    NAL_UNIT_UNSPECIFIED_57 = 57
    NAL_UNIT_UNSPECIFIED_58 = 58
    NAL_UNIT_UNSPECIFIED_59 = 59
    NAL_UNIT_UNSPECIFIED_60 = 60
    NAL_UNIT_UNSPECIFIED_61 = 61
    NAL_UNIT_UNSPECIFIED_62 = 62
    NAL_UNIT_UNSPECIFIED_63 = 63
    NAL_UNIT_INVALID = 64

class slice_segment_header(object):
    def __init__(self, s):
        """
        7.3.6.1 General slice segment header syntax
        """
        pass
    def show(self):
        pass

class slice_segment_data(object):
    def __init__(self, s):
        """
        """
        pass
    def show(self):
        pass

class rbsp_slice_segment_trailing_bits(object):
    def __init__(self, s):
        """
        """
        pass
    def show(self):
        pass

class hrd_parameters(object):
    def __init__(self, s, commonInfPresentFlag, maxNumSubLayersMinus1):
        """
        E.2.2 HRD parameters syntax
        """
        self.t='\t\t'
        if commonInfPresentFlag:
            self.nal_hrd_parameters_present_flag = s.read('uint:1')
            self.vcl_hrd_parameters_present_flag = s.read('uint:1')
            if self.nal_hrd_parameters_present_flag or self.vcl_hrd_parameters_present_flag:
                self.sub_pic_hrd_params_present_flag = s.read('uint:1')
                if self.sub_pic_hrd_params_present_flag:
                    self.tick_divisor_minus2 = s.read('uint:8')
                    self.du_cpb_removal_delay_increment_length_minus1 = s.read('uint:5')
                    self.sub_pic_cpb_params_in_pic_timing_sei_flag = s.read('uint:1')
                    self.dpb_output_delay_du_length_minus1 = s.read('uint:5')
                self.bit_rate_scale = s.read('uint:4')
                self.cpb_size_scale = s.read('uint:4')
                if self.sub_pic_hrd_params_present_flag:
                    self.icpb_size_du_scale = s.read('uint:4')
                self.initial_cpb_removal_delay_length_minus1 = s.read('uint:5')
                self.au_cpb_removal_delay_length_minus1 = s.read('uint:5')
                self.dpb_output_delay_length_minus1 = s.read('uint:5')
        for i in range(maxNumSubLayersMinus1 + 1):
            self.fixed_pic_rate_general_flag[ i ] = s.read('uint:1')
            if not self.fixed_pic_rate_general_flag[i]:
                self.fixed_pic_rate_within_cvs_flag[i] = s.read('uint:1')
            if self.fixed_pic_rate_within_cvs_flag[i]:
                self.elemental_duration_in_tc_minus1[i] = s.read('ue')
            else:
                self.low_delay_hrd_flag[i] = s.read('uint:1')
            if not self.low_delay_hrd_flag[i]:
                self.cpb_cnt_minus1[i] = s.read('ue')
            if self.nal_hrd_parameters_present_flag:
                sub_layer_hrd_parameters(s, i)
            if self.vcl_hrd_parameters_present_flag:
                self.sub_layer_hrd_parameters(s,i)

    def show(self):
        """
        """
        attrs = vars(self)
        print self.t,'hrd parameters'
        print self.t,'=============='
        for k, v in attrs.iteritems():
            print k, v

class slice_segment_layer_rbsp(object):
    def __init__(self, s):
        """
        Interpret next bits in BitString s as an ...
        7.3.2.9 Slice segment layer RBSP syntax
        """
        self.t = '\t'
        slice_segment_header(s).show()
        slice_segment_data(s).show()
        rbsp_slice_segment_trailing_bits(s)

    def show(self):
        pass

class video_parameter_set_rbsp(object):
    def __init__(self, s):
        """
        Interpret next bits in BitString s as an VPS
        7.3.2.1 Video parameter set RBSP syntax
        """
        self.t = '\t'
        self.vps_video_parameter_set_id = s.read('uint:4')
        self.vps_reserved_three_2bits = s.read('uint:2')
        self.vps_max_layers_minus1 = s.read('uint:6')
        self.vps_max_sub_layers_minus1 = s.read('uint:3')
        self.vps_temporal_id_nesting_flag = s.read('uint:1')
        self.vps_reserved_0xffff_16bits = s.read('uint:16')

        self.ptl = profile_tier_level(s, self.vps_max_sub_layers_minus1)

        self.vps_sub_layer_ordering_info_present_flag = s.read('uint:1')
        i = 0 if self.vps_sub_layer_ordering_info_present_flag else self.vps_max_sub_layers_minus1
        self.vps_max_dec_pic_buffering_minus1 = []
        self.vps_max_num_reorder_pics = []
        self.vps_max_latency_increase_plus1 = []
        for n in range(self.vps_max_sub_layers_minus1 + 1):
            self.vps_max_dec_pic_buffering_minus1.append(s.read('ue'))
            self.vps_max_num_reorder_pics.append(s.read('ue'))
            self.vps_max_latency_increase_plus1.append(s.read('ue'))
        self.vps_max_layer_id = s.read('uint:1')
        self.vps_num_layer_sets_minus1 = s.read('uint:1')
        for i in range(self.vps_num_layer_sets_minus1 + 1):
            for j in range(self.vps_max_layer_id + 1):
                #layer_id_included_flag[ i ][ j ]
                s.read('uint:1')


        self.vps_timing_info_present_flag = s.read('uint:1')
        if self.vps_timing_info_present_flag:
            self.vps_num_units_in_tick = s.read('uint:1')
            self.vps_time_scale = s.read('uint:1')
            self.vps_poc_proportional_to_timing_flag = s.read('uint:1')
            if self.vps_poc_proportional_to_timing_flag:
                self.vps_num_ticks_poc_diff_one_minus1 = s.read('uint:1')
            self.vps_num_hrd_parameters = s.read('uint:1')
            self.hrd_layer_set_idx = []
            self.cprms_present_flag = []
            for i in range(self.vps_num_hrd_parameters):
                self.hrd_layer_set_idx.append(s.read('ue'))
                if i > 0:
                    cprms_present_flag.append(s.read('uint:1'))
                    self.hrdp = hrd_parameters(cprms_present_flag[i], self.vps_max_sub_layers_minus1)
        self.vps_extension_flag = s.read('uint:1')
#        if self.vps_extension_flag:
#        while( more_rbsp_data( ) )
#        vps_extension_data_flag
#        rbsp_trailing_bits( )

    def show(self):
        print
        print self.t,'Video parameter Set RBSP'
        print self.t,'========================'
        print self.t,'vps_video_parameter_set_id', self.vps_video_parameter_set_id
        print self.t,'vps_reserved_three_2bits', self.vps_reserved_three_2bits
        print self.t,'vps_max_layers_minus1', self.vps_max_layers_minus1
        print self.t,'vps_max_sub_layers_minus1', self.vps_max_sub_layers_minus1
        print self.t,'vps_temporal_id_nesting_flag', self.vps_temporal_id_nesting_flag
        print self.t,'vps_reserved_0xffff_16bits', self.vps_reserved_0xffff_16bits

        self.ptl.show()

        print
        print self.t, 'vps_sub_layer_ordering_info_present_flag', self.vps_sub_layer_ordering_info_present_flag
        for n in range(self.vps_max_sub_layers_minus1 + 1):
            print self.t, 'vps_max_dec_pic_buffering_minus1', self.vps_max_dec_pic_buffering_minus1
            print self.t, 'vps_max_num_reorder_pics', self.vps_max_num_reorder_pics
            print self.t, 'vps_max_latency_increase_plus1', self.vps_max_latency_increase_plus1
        print self.t, 'vps_max_layer_id', self.vps_max_layer_id
        print self.t, 'vps_num_layer_sets_minus1', self.vps_num_layer_sets_minus1
        for i in range(self.vps_num_layer_sets_minus1 + 1):
            for j in range(self.vps_max_layer_id + 1):
                #layer_id_included_flag[ i ][ j ]
                pass

        print self.t, 'vps_timing_info_present_flag', self.vps_timing_info_present_flag
        if self.vps_timing_info_present_flag:
            print self.t, 'vps_num_units_in_tick', self.vps_num_units_in_tick
            print self.t, 'vps_time_scale', self.vps_time_scale
            print self.t, 'vps_poc_proportional_to_timing_flag', self.vps_poc_proportional_to_timing_flag
            if self.vps_poc_proportional_to_timing_flag:
                print self.t, 'vps_num_ticks_poc_diff_one_minus1', self.vps_num_ticks_poc_diff_one_minus1
            print self.t, 'vps_num_hrd_parameters', self.vps_num_hrd_parameters
            for i in range(self.vps_num_hrd_parameters):
                self.hrd_layer_set_idx.append(s.read('ue'))
                if i > 0:
                    cprms_present_flag.append(s.read('uint:1'))
                    self.hrdp.show()
        print self.t, 'vps_extension_flag', self.vps_extension_flag

class profile_tier_level(object):
    def __init__(self, s, maxNumSubLayersMinus1):
        """
        Interpret next bits in BitString s as an profile_tier_level
        7.3.3 Profile, tier and level syntax
        """
        self.t = '\t\t'
        self.general_profile_space = s.read('uint:2')
        self.general_tier_flag = s.read('uint:1')
        self.general_profile_idc = s.read('uint:5')
        self.general_profile_compatibility_flag = [s.read('uint:1') for _ in range(32)]
        self.general_progressive_source_flag = s.read('uint:1')
        self.general_interlaced_source_flag = s.read('uint:1')
        self.general_non_packed_constraint_flag = s.read('uint:1')
        self.general_frame_only_constraint_flag = s.read('uint:1')
        self.general_reserved_zero_44bits = s.read('uint:44')
        self.general_level_idc = s.read('uint:8')
        self.sub_layer_profile_present_flag = []
        self.sub_layer_level_present_flag = []
        for i in range(maxNumSubLayersMinus1):
            self.sub_layer_profile_present_flag.append(s.read('uint:1'))
            self.sub_layer_level_present_flag.append(s.read('uint:1'))

    def show(self):
        print
        print self.t,'Profile Tier Level'
        print self.t,'=================='
        print self.t,'general_profile_space', self.general_profile_space
        print self.t,'general_tier_flag', self.general_tier_flag
        print self.t,'general_profile_idc', self.general_profile_idc
        for i in range(32):
            print "{}{}[{:2d}] {}".format(self.t, 'general_profile_compatibility_flag', i, self.general_profile_compatibility_flag[i])
        print self.t,'general_progressive_source_flag', self.general_progressive_source_flag
        print self.t,'general_interlaced_source_flag', self.general_interlaced_source_flag
        print self.t,'general_non_packed_constraint_flag', self.general_non_packed_constraint_flag
        print self.t,'general_frame_only_constraint_flag', self.general_frame_only_constraint_flag
        print self.t,'general_reserved_zero_44bits', self.general_reserved_zero_44bits
#        print self.t,"{0:b}".format(self.general_reserved_zero_44bits)
        print self.t,'general_level_idc', self.general_level_idc
        print self.t,'sub_layer_profile_present_flag', self.sub_layer_profile_present_flag
        print self.t,'sub_layer_level_present_flag', self.sub_layer_level_present_flag

class seq_parameter_set_rbsp(object):
    def __init__(self, s):
        """
        Interpret next bits in BitString s as an SPS
        7.3.2.2 Sequence parameter set RBSP syntax
        """
        self.t = '\t'
        self.sps_video_parameter_set_id = s.read('uint:4')
        self.sps_max_sub_layers_minus1 = s.read('uint:1')
        self.sps_temporal_id_nesting_flag = s.read('uint:1')

        self.ptl = profile_tier_level(s, self.sps_max_sub_layers_minus1)

    def show(self):
        print
        print self.t,'Sequence Parameter Set RBSP'
        print self.t,'==========================='
        print self.t,'sps_video_parameter_set_id', self.sps_video_parameter_set_id
        print self.t,'sps_max_sub_layers_minus1', self.sps_max_sub_layers_minus1
        print self.t,'sps_temporal_id_nesting_flag', self.sps_temporal_id_nesting_flag

        self.ptl.show()


class pic_parameter_set_rbsp(object):
    def __init__(self, s):
        """
        Interpret next bits in BitString s as an PPS
        7.3.2.3 Picture parameter set RBSP syntax
        """
        self.t='\t'
        self.pps_pic_parameter_set_id = s.read('ue')
        self.pps_seq_parameter_set_id = s.read('ue')
        self.dependent_slice_segments_enabled_flag = s.read('uint:1')
        self.output_flag_present_flag = s.read('uint:1')
        self.num_extra_slice_header_bits = s.read('uint:3')
        self.sign_data_hiding_enabled_flag = s.read('uint:1')
        self.cabac_init_present_flag = s.read('uint:1')
        self.num_ref_idx_l0_default_active_minus1 = s.read('ue')
        self.num_ref_idx_l1_default_active_minus1 = s.read('ue')
        self.init_qp_minus26 = s.read('se')
        self.constrained_intra_pred_flag = s.read('uint:1')
        self.transform_skip_enabled_flag = s.read('uint:1')
        self.cu_qp_delta_enabled_flag = s.read('uint:1')
        if self.cu_qp_delta_enabled_flag:
            self.diff_cu_qp_delta_depth = s.read('ue')
        self.pps_cb_qp_offset = s.read('se')
        self.pps_cr_qp_offset = s.read('se')
        self.pps_slice_chroma_qp_offsets_present_flag = s.read('uint:1')
        self.weighted_pred_flag = s.read('uint:1')
        self.weighted_bipred_flag = s.read('uint:1')
        self.transquant_bypass_enabled_flag = s.read('uint:1')
        self.tiles_enabled_flag = s.read('uint:1')
        self.entropy_coding_sync_enabled_flag = s.read('uint:1')

        if self.tiles_enabled_flag:
            self.num_tile_columns_minus1 = s.read('ue')
            self.num_tile_rows_minus1 = s.read('ue')
            self.uniform_spacing_flag = s.read('uint:1')
            if not self.uniform_spacing_flag:
                self.column_width_minus1 = [s.read('ue') for _ in range(self.num_tile_columns_minus1)]
                self.row_height_minus1 = [s.read('ue') for _ in range(self.num_tile_rows_minus1)]
            self.loop_filter_across_tiles_enabled_flagi = s.read('uint:1')
        self.pps_loop_filter_across_slices_enabled_flag = s.read('uint:1')
        self.deblocking_filter_control_present_flag = s.read('uint:1')
        if self.deblocking_filter_control_present_flag:
            self.deblocking_filter_override_enabled_flag = s.read('uint:1')
            self.pps_deblocking_filter_disabled_flag = s.read('uint:1')
            if not self.pps_deblocking_filter_disabled_flag:
                self.pps_beta_offset_div2 = s.read('se')
                self.pps_tc_offset_div2 = s.read('se')
        self.pps_scaling_list_data_present_flag = s.read('uint:1')
        if self.pps_scaling_list_data_present_flag:
            scaling_list_data(s)
        self.lists_modification_present_flag = s.read('uint:1')
        self.log2_parallel_merge_level_minus2 = s.read('ue')
        self.slice_segment_header_extension_present_flag = s.read('uint:1')
        self.pps_extension_flag = s.read('uint:1')
#        if self.pps_extension_flag:
#            while more_rbsp_data():
#                self.pps_extension_data_flag = s.read('uint:1')
#        rbsp_trailing_bits()

    def show(self):
        print
        print self.t,'Picture Parameter Set RBSP'
        print self.t,'=========================='
        print self.t,'pps_pic_parameter_set_id', self.pps_pic_parameter_set_id
        print self.t,'pps_seq_parameter_set_id', self.pps_seq_parameter_set_id
        print self.t,'dependent_slice_segments_enabled_flag', self.dependent_slice_segments_enabled_flag
        print self.t,'output_flag_present_flag', self.output_flag_present_flag
        print self.t,'num_extra_slice_header_bits', self.num_extra_slice_header_bits
        print self.t,'sign_data_hiding_enabled_flag', self.sign_data_hiding_enabled_flag
        print self.t,'cabac_init_present_flag', self.cabac_init_present_flag
        print self.t,'num_ref_idx_l0_default_active_minus1', self.num_ref_idx_l0_default_active_minus1
        print self.t,'num_ref_idx_l1_default_active_minus1', self.num_ref_idx_l1_default_active_minus1
        print self.t,'init_qp_minus26', self.init_qp_minus26
        print self.t,'constrained_intra_pred_flag', self.constrained_intra_pred_flag
        print self.t,'transform_skip_enabled_flag', self.transform_skip_enabled_flag
        print self.t,'cu_qp_delta_enabled_flag', self.cu_qp_delta_enabled_flag
        if self.cu_qp_delta_enabled_flag:
            print self.t,'diff_cu_qp_delta_depth', self.diff_cu_qp_delta_depth
        print self.t,'pps_cb_qp_offset', self.pps_cb_qp_offset
        print self.t,'pps_cr_qp_offset', self.pps_cr_qp_offset
        print self.t,'pps_slice_chroma_qp_offsets_present_flag', self.pps_slice_chroma_qp_offsets_present_flag
        print self.t,'weighted_pred_flag', self.weighted_pred_flag
        print self.t,'weighted_bipred_flag', self.weighted_bipred_flag
        print self.t,'transquant_bypass_enabled_flag', self.transquant_bypass_enabled_flag
        print self.t,'tiles_enabled_flag', self.tiles_enabled_flag
        print self.t,'entropy_coding_sync_enabled_flag', self.entropy_coding_sync_enabled_flag

        if self.tiles_enabled_flag:
            print self.t, 'num_tile_columns_minus1', self.num_tile_columns_minus1
            print self.t, 'num_tile_rows_minus1', self.num_tile_rows_minus1
            print self.t, 'uniform_spacing_flag', self.uniform_spacing_flag
            if not self.uniform_spacing_flag:
                print self.t, 'column_width_minus1', self.column_width_minus1
                print self.t, 'row_height_minus1', self.row_height_minus1
            print self.t, 'loop_filter_across_tiles_enabled_flagi', self.loop_filter_across_tiles_enabled_flagi
        print self.t, 'pps_loop_filter_across_slices_enabled_flag', self.pps_loop_filter_across_slices_enabled_flag
        print self.t, 'deblocking_filter_control_present_flag', self.deblocking_filter_control_present_flag
        if self.deblocking_filter_control_present_flag:
            print self.t, 'deblocking_filter_override_enabled_flag', self.deblocking_filter_override_enabled_flag
            print self.t, 'pps_deblocking_filter_disabled_flag', self.pps_deblocking_filter_disabled_flag
            if not self.pps_deblocking_filter_disabled_flag:
                print self.t, 'pps_beta_offset_div2', self.pps_beta_offset_div2
                print self.t, 'pps_tc_offset_div2', self.pps_tc_offset_div2
        print self.t, 'pps_scaling_list_data_present_flag', self.pps_scaling_list_data_present_flag
        if self.pps_scaling_list_data_present_flag:
            scaling_list_data(s)
        print self.t, 'lists_modification_present_flag', self.lists_modification_present_flag
        print self.t, 'log2_parallel_merge_level_minus2', self.log2_parallel_merge_level_minus2
        print self.t, 'slice_segment_header_extension_present_flag', self.slice_segment_header_extension_present_flag
        print self.t, 'pps_extension_flag', self.pps_extension_flag

class nal_unit_header(object):
    def __init__(self, s):
        """
        Interpret next bits in BitString s as a nal_unit
        """
        self.forbidden_zero_bit  = s.read('uint:1')
        self.nal_unit_type = s.read('uint:6')
        self.nuh_layer_id = s.read('uint:6')
        self.nuh_temporal_id_plus1 = s.read('uint:3')

    def show(self):
        print 'forbidden_zero_bit', self.forbidden_zero_bit
        print 'nal_unit_type', self.nal_unit_type
        print 'nuh_layer_id', self.nuh_layer_id
        print 'nuh_temporal_id_plus1', self.nuh_temporal_id_plus1


def read_nal_unit(s, i, NumBytesInNalUnit):
    """
    Table 7-1 - NAL unit type codes and NAL unit type classes
    """
    # Advance pointer and skip 24 bits, i.e. 0x000001
    s.pos = i + 24

    n = nal_unit_header(s)
    n.show()

    # 7.3.1.1
    # Convert NAL data (Annex B format) to RBSP data
    NumBytesInRbsp = 0
    rbsp_byte = BitStream()
    for i in xrange(NumBytesInNalUnit):
        if (i+2) < NumBytesInNalUnit and s.peek('bits:24') == '0x000003':
            rbsp_byte.append(s.read('bits:8'))
            rbsp_byte.append(s.read('bits:8'))
            # emulation_prevention_three_byte
            s.read('bits:8')
        else:
            rbsp_byte.append(s.read('bits:8'))

    NumBytesInRbsp = len(rbsp_byte)
    s = rbsp_byte

    nal_unit_type = n.nal_unit_type

    if nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_TRAIL_N or \
       nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_TRAIL_R:
        # Coded slice segment of a non-TSA, non-STSA trailing picture
        slice_segment_layer_rbsp(s).show()
    elif nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_TSA_N or \
         nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_TSA_R:
        # Coded slice segment of a TSA picture
        slice_segment_layer_rbsp(s)
    elif nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_STSA_N or \
         nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_STSA_R:
        # Coded slice segment of an STSA picture
        slice_segment_layer_rbsp(s).show()
    elif nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_RADL_N or \
         nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_RADL_R:
        # Coded slice segment of a RADL picture
        slice_segment_layer_rbsp(s).show()
    elif nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_RASL_N or \
         nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_RASL_R:
        # Coded slice segment of a RADL picture
        slice_segment_layer_rbsp(s).show()
    elif nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL_N10 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL_N12 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL_N14:
        # Reserved non-IRAP sub-layer non-reference VCL NAL unit types
        pass
    elif nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL_R11 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL_R13 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL_R15:
        # Reserved non-IRAP sub-layer reference VCL NAL unit types
        pass
    elif nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_BLA_W_LP or \
         nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_BLA_W_RADL or \
         nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_BLA_N_LP:
        # Coded slice segment of a BLA picture
        slice_segment_layer_rbsp(s).show()
    elif nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_IDR_W_RADL or \
         nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_IDR_N_LP:
        # Coded slice segment of an IDR picture
        slice_segment_layer_rbsp(s).show()
    elif nal_unit_type == NalUnitType.NAL_UNIT_CODED_SLICE_CRA:
        # Coded slice segment of a CRA picture
        slice_segment_layer_rbsp(s).show()
    elif nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_IRAP_VCL22 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_IRAP_VCL23:
        # Reserved IRAP VCL NAL unit types
        pass
    elif nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL24 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL25 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL26 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL27 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL28 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL29 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL30 or \
         nal_unit_type == NalUnitType.NAL_UNIT_RESERVED_VCL31:
        #Reserved non-IRAP VCL NAL unit types
        pass
    elif nal_unit_type == NalUnitType.NAL_UNIT_VPS:
        # Video parameter set
        video_parameter_set_rbsp(s).show()
    elif nal_unit_type == NalUnitType.NAL_UNIT_SPS:
        # Sequence parameter set
        seq_parameter_set_rbsp(s).show()
    elif nal_unit_type == NalUnitType.NAL_UNIT_PPS:
        # Picture parameter set
        pic_parameter_set_rbsp(s).show()

def main():
    """
    """
    F = 'bqmall.bin'

    s = BitStream(filename=F)

    nals = list(s.findall('0x000001', bytealigned=True))
    size = [y - x for x,y in zip(nals,nals[1:])]

    for i, n in zip(nals, size):
        print
        print "!! Found NAL @ offset {0:d} ({0:#x})".format((i+24)/8)
        read_nal_unit(s, i, n/8) # bits to bytes

if __name__ == "__main__":
    main()
