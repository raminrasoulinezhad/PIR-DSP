##############################################################
# SeyedRamin Rasoulinezhad
# Seyedramin.rasoulinezhad@sydney.edu.au
#
# This app automatically generates a multiplier regarding our research
#
##############################################################

import numpy as np

class multiplier:
    def __init__(self, A_width, B_width, A_chop_factor, B_chop_factor, level, output_directory):

        self.set_output_directory(output_directory)

        self.A_width = A_width
        self.B_width = B_width

        self.chop(A_chop_factor, B_chop_factor)
        self.fracture(level)

        self.A_roots, self.A_roots_len, self.A_result, self.A_result_mult_size, self.A_exception = self.fraction_points(
            self.A_chop_size, self.fraction_level)
        self.B_roots, self.B_roots_len, self.B_result, self.B_result_mult_size, self.B_exception = self.fraction_points(
            self.B_chop_size, self.fraction_level)

        self.A_roots_maxFraction, self.A_roots_len_maxFraction, self.A_result_maxFraction, self.A_result_mult_size_maxFraction, self.A_exception_maxFraction = self.fraction_points(self.A_chop_size, self.fraction_level_maxFraction)
        self.B_roots_maxFraction, self.B_roots_len_maxFraction, self.B_result_maxFraction, self.B_result_mult_size_maxFraction, self.B_exception_maxFraction = self.fraction_points(self.B_chop_size, self.fraction_level_maxFraction)


        self.arch, self.arch_shift, self.arch_splitters, self.arch_splitters_maxFraction, self.arch_masker, self.arch_masker_maxFraction, self.arch_SIMD_hight, self.arch_Saving_precision_SE_size = self.Architecture()
        print(self.arch_masker)
        print(self.arch_masker_maxFraction)
        print(self.arch_splitters)
        print(self.arch_splitters_maxFraction)

        #print (self.arch, self.arch_shift, self.arch_splitters, self.arch_masker, self.arch_SIMD_hight, self.arch_Saving_precision_SE_size)

        self.set_test_max_counter(10000)

        self.details()

        self.parameter_optimization_F0 = 1
        self.parameter_optimization_pipeline = 1
        self.parameter_optimization_carry_look_ahead = 1
        self.parameter_optimization_parallelism_T = 1
        self.parameter_optimization_ALU_CarryLookAHead = 0     # it's not good


    def set_output_directory(self, directory):
        # to set directory for output files
        self.output_directory = directory

    def set_test_max_counter(self, test_max_counter):
        # to set test_max_counter for test bench process
        self.test_max_counter = test_max_counter

    def details(self):
        # Print all multiplier attributes
        print('------------------------------------------------------------')
        print('|\tThe multiplier details are:')
        print('|\tA_width:', self.A_width)
        print('|\tB_width:', self.B_width)
        print('|\tA_chop_size:', self.A_chop_size)
        print('|\tB_chop_size:', self.B_chop_size)
        print('|\tA_chop_number:', self.A_chop_number)
        print('|\tB_chop_number:', self.B_chop_number)
        print('|\tfraction_level:', self.fraction_level)
        print('|\tsupported_multipliers_list:', self.supported_multipliers_list)
        print('|\toutput_directory:', self.output_directory)
        print('------------------------------------------------------------')

    def chop(self, A_chop_factor, B_chop_factor):
        # this method check if the chop factor is OK and set it as a class variable
        if(not self.dividable(self.A_width, A_chop_factor)):
            raise NameError('$$ Error: A is not dividable. A:', self.A_width, 'A_chop_number: ', A_chop_factor)

        if(not self.dividable(self.B_width, B_chop_factor)):
            raise NameError('$$ Error: B is not dividable. B:', self.B_width, 'B_chop_number: ', B_chop_factor)

        # Also, the widest number should be A # to have fractions
        if (self.A_width/A_chop_factor < self.B_width/B_chop_factor):
            temp = self.B_width
            self.B_width = self.A_width
            self.A_width = temp

            temp = B_chop_factor
            B_chop_factor = A_chop_factor
            A_chop_factor = temp
            print('***********************************')
            print('* Warning: We replaced A and B !! *')
            print('***********************************')

        self.supported_multipliers_list = [[self.A_width, self.B_width]]

        # set the class parameters
        self.A_chop_size = np.int(self.A_width/A_chop_factor)
        self.B_chop_size = np.int(self.B_width/B_chop_factor)

        self.A_chop_number = A_chop_factor
        self.B_chop_number = B_chop_factor
        self.T_chop_number = self.A_chop_number * self.B_chop_number

        # update multiplier capability list
        self.supported_multipliers_list.append([[self.A_chop_size, self.B_chop_size]])

    def fracture(self, level):
        # this method check if the fracture factor is OK and set it as a class variable
        A_chop_size_temp = self.A_chop_size
        B_chop_size_temp = self.B_chop_size
        supported_multipliers_list = []

        inputs_are_OK = 1
        for i in range (0, level):
            A_chop_size_temp = np.int(np.floor(A_chop_size_temp / 2))
            B_chop_size_temp = np.int(np.floor(B_chop_size_temp / 2))
            supported_multipliers_list.append([A_chop_size_temp, B_chop_size_temp])

            if (not (A_chop_size_temp >= 2)):
                print('level is not OK for input A')
                inputs_are_OK = 0

            if (not(B_chop_size_temp >= 2)):
                print('level is not OK for input B')
                inputs_are_OK = 0

        if (inputs_are_OK == 0):
            raise NameError('$$ Error: Fracture factor is NOT OK. Please reduce this factor')
        else:
            # set the class parameters
            self.fraction_level = level
            for i in range(0, level):
                # update multiplier capability list
                self.supported_multipliers_list[1].append(supported_multipliers_list[i])

            while (inputs_are_OK):
                self.fraction_level_maxFraction = level
                A_chop_size_temp = np.int(np.floor(A_chop_size_temp / 2))
                B_chop_size_temp = np.int(np.floor(B_chop_size_temp / 2))
                if (not (A_chop_size_temp >= 2)):
                    inputs_are_OK = 0
                if (not (B_chop_size_temp >= 2)):
                    inputs_are_OK = 0
                level = level + 1

        return

    def dividable(self, a, b):
        # True if 'a' can be divided by 'b'
        return (a % b == 0)

    def fraction_points(self, width, level):
        # this method extract some critical parameters
        #   roots       = the length of each sub multiplier corner in a square
        #   len(roots)  = length of root array
        #   result      = the corners location in one dimension
        #   result_mult_size   = size of multiplier
        #   exception   = an array of 1/0. if an element is 1 --> in that level multipliers are tightly close
        result = []
        result_mult_size = []
        exception = []

        roots = []
        root = width
        for counter in range(0, level):
            root_half = np.int(np.floor(root/2))
            root_diff = np.int(root - root_half)
            roots_appendix = []
            for i in range(0, len(roots)):
                roots_appendix.append(np.int(roots[i]-root_diff))
            for i in range(0, len(roots_appendix)):
                roots.append(roots_appendix[i])
            roots.append(root)
            root = root_half

        roots.append(root)
        roots = sorted(roots, reverse=True)

        exception.append(np.mod(width, 2)*(-1)+1)
        for counter in range(0, level+1):
            result_temp = []
            for i in range(0,len(roots), pow(2, level-counter)):
                result_temp.append(roots[i])

            result.append(result_temp)
            result_mult_size.append(min(result_temp))
            if (not(counter == 0)):
                exception.append(np.mod(result_mult_size[counter-1], 2)*(-1)+1)

        return roots, len(roots), result, result_mult_size, exception

    def Architecture(self):
        # this method use the chop numbers
        a_dimension = self.A_chop_number
        b_dimension = self.B_chop_number

        a_ch_size = self.A_chop_size
        b_ch_size = self.B_chop_size

        if ((a_dimension == 3)&( b_dimension == 3)):
            arch = [[0, 1, 4], [2, 3, 6], [5, 7, 8]]
            arch_shift = [[0, -b_ch_size, 0], [-b_ch_size, 0, b_ch_size], [0, b_ch_size, 0]]

            arch_splitters = [1 * a_ch_size + 1 * b_ch_size, 2 * a_ch_size + 2 * b_ch_size, 3 * a_ch_size + 3 * b_ch_size]
            arch_masker_size = 3 * pow(2, self.fraction_level)
            arch_SIMD_hight = 3

        elif ((a_dimension == 3)&( b_dimension == 2)):
            arch = [[0, 1, 4], [2, 3, 5]]
            arch_shift = [[b_ch_size, 0, b_ch_size], [0, b_ch_size, 0]]

            arch_splitters = [1 * a_ch_size + 2 * b_ch_size, 2 * a_ch_size + 3 * b_ch_size]
            arch_masker_size = pow(2, self.fraction_level + 1)
            arch_SIMD_hight = 3

        elif ((a_dimension == 2)&( b_dimension == 2)):
            arch = [[0, 1], [2, 3]]
            arch_shift = [[0, -b_ch_size], [b_ch_size, 0]]

            arch_splitters = [1 * a_ch_size + 1 * b_ch_size, 2 * a_ch_size + 2 * b_ch_size]
            arch_masker_size = pow(2, self.fraction_level + 1)
            arch_SIMD_hight = 2

        elif ((a_dimension == 2) & (b_dimension == 1)):
            arch = [[0, 1]]
            arch_shift = [[self.A_chop_size, 0]]

            arch_splitters = [2 * a_ch_size + 1 * b_ch_size]
            arch_masker_size = pow(2, self.fraction_level+ 1)
            arch_SIMD_hight = 2

        elif ((a_dimension == 1) & (b_dimension == 2)):
            arch = [[0], [1]]
            arch_shift = [[self.B_chop_size], [0]]

            arch_splitters = [1 * a_ch_size + 2 * b_ch_size]
            arch_masker_size = pow(2, self.fraction_level+ 1)
            arch_SIMD_hight = 2
        elif ((a_dimension == 1) & (b_dimension == 1)):
            arch = [[0]]
            arch_shift = [[0]]

            arch_splitters = [1 * a_ch_size + 1 * b_ch_size]
            arch_masker_size = pow(2, self.fraction_level + 1)
            arch_SIMD_hight = 1
        else:
            raise NameError('$$ Error: architecture is not registered in method "Architecture". Please change "A_chop_number" or/and "B_chop_number"')


        arch_splitters_in_a_sub_multiplier = [x + y for x, y in zip(self.A_roots, self.B_roots)]
        arch_splitters_in_a_sub_multiplier_maxFraction = [x + y for x, y in zip(self.A_roots_maxFraction, self.B_roots_maxFraction)]

        total_arch_splitters = []
        for j in arch_splitters:
            for i in arch_splitters_in_a_sub_multiplier:
                total_arch_splitters.append(j-(self.A_chop_size+self.B_chop_size - i) - 1)

        total_arch_splitters_maxFraction = []
        for j in arch_splitters:
            for i in arch_splitters_in_a_sub_multiplier_maxFraction:
                total_arch_splitters_maxFraction.append(j - (self.A_chop_size + self.B_chop_size - i) - 1)

        arch_splitters = sorted(total_arch_splitters, reverse=False)
        arch_splitters_maxFraction = sorted(total_arch_splitters_maxFraction, reverse=False)

        arch_masker = np.empty(arch_masker_size, dtype=object)
        print(arch_masker)
        for level in range(0, self.fraction_level + 1):
            print(level)

            #step = np.int(arch_masker_size / pow(2, level + 1))############
            #step = np.int(pow(2, self.fraction_level_maxFraction - level))
            step = np.int(pow(2, self.fraction_level - level))


            print(step)
            index = step - 1
            print(self.fraction_level)
            for counter in range(0, np.int(arch_masker_size / pow(2, self.fraction_level - level))):
                if (arch_masker[index] == None):
                    arch_masker[index] = 'HALF_' + str(level)
                else:
                    arch_masker[index] = self.boolian_or(arch_masker[index], 'HALF_' + str(level))
                index = index + step

        arch_masker_maxFraction = arch_masker
        for i in range(self.fraction_level_maxFraction - self.fraction_level):
            temp = []
            for j in arch_masker_maxFraction:
                temp.append('')
                temp.append(j)
            arch_masker_maxFraction = temp

        arch_Saving_precision_SE_size = np.int(np.ceil(np.log2(np.max([2, arch_SIMD_hight]))))

        return arch, arch_shift, arch_splitters, arch_splitters_maxFraction, arch_masker, arch_masker_maxFraction, arch_SIMD_hight, arch_Saving_precision_SE_size


    # these method make a boolean string by boolean strings as inputs
    def boolian_not(self, signal1):
        return '~('+signal1+')'
    def boolian_and(self, signal1, signal2):
        return '('+signal1+')&('+ signal2 +')'
    def boolian_nand(self, signal1, signal2):
        return '~(('+signal1+')&('+ signal2 +'))'
    def boolian_or(self, signal1, signal2):
        return '('+signal1+')|('+ signal2 +')'
    def boolian_nor(self, signal1, signal2):
        return '~(('+signal1+')|('+ signal2 +'))'
    def boolian_xor(self, signal1, signal2):
        return '('+signal1+')^('+ signal2 +')'
    def boolian_xnor(self, signal1, signal2):
        return '~(('+signal1+')^('+ signal2 +'))'
    def boolian_masker(self, signal1, signal2):
        return '('+signal1+')&(~('+ signal2 +'))'
    def boolian_controlled_not(self, signal1, signal2):
        return '('+signal1+')^('+ signal2 +')'
    def boolian_mux(self, signal1, signal2, selector):
        selector_not = self.boolian_not(selector)
        temp0 = self.boolian_and(signal1, selector_not)
        temp1 = self.boolian_and(signal2, selector)
        return (self.boolian_or(temp0, temp1))

    def wall_points_finder(self):
        wall_points = []
        for level in range(0, self.fraction_level + 1):
            for component_a in range(0, len(self.A_result[level])):
                for component_b in range(0, len(self.B_result[level])):
                    if (component_a == component_b):
                        i_index = self.B_result[level][component_b]
                        j_index = self.A_result[level][component_a]
                        wall_points.append(i_index + j_index)

        wall_points = np.sort(list(set(wall_points)))
        return wall_points

    def writer_module_chopped_input(self, file):
        if (self.parameter_optimization_pipeline):
            file.write('\t\tinput clk,\n')
            file.write('\t\tinput reset,\n')
            file.write('\n')
        file.write('\t\tinput [A_chop_size-1:0] A,\n')
        file.write('\t\tinput [B_chop_size-1:0] B,\n')
        file.write('\n')
        file.write('\t\tinput A_sign,\n')
        file.write('\t\tinput B_sign,\n')
        file.write('\n')

        for i in range(0, self.fraction_level+1):
            file.write(
                '\t\tinput HALF_' + str(i) + ',\t// a selector bit to switch computation to half mode level ' + str(
                    i) + '\n')
        file.write('\n')

        file.write('\t\toutput reg [A_chop_size+B_chop_size-1:0] C\n')
        #file.write('\t\toutput reg [A_chop_size+B_chop_size-1:0] C_0,\n')
        #file.write('\t\toutput reg [A_chop_size+B_chop_size-1:0] C_1\n')
        file.write('\t);\n')
        file.write('\n')

        file.write('parameter A_chop_size = ' + str(self.A_chop_size) + ';\n')
        file.write('parameter B_chop_size = ' + str(self.B_chop_size) + ';\n')
        file.write('\n')

    def writer_input_sign_extended(self, file):
        # sign extension signals which are controlled by A_sign and B_sign
        file.write('// to support both signed and unsigned multiplication\n')
        file.write('// sign extension regarding extra sign identifier\n')
        for i in range(0, self.fraction_level + 1):
            for j in range(0, pow(2, i)):
                wire_temp_name_A = 'A_extended_level' + str(i) + '_' + str(j)
                wire_temp_name_B = 'B_extended_level' + str(i) + '_' + str(j)
                file.write('wire ' + wire_temp_name_A + ';\n')
                file.write('wire ' + wire_temp_name_B + ';\n')

                A_index = str(self.A_roots[np.int(j * self.A_roots_len / pow(2, i))] - 1)
                temp = 'A[' + A_index + ']'
                temp = self.boolian_and(temp, 'A_sign')
                file.write('assign ' + wire_temp_name_A + ' = ' + temp + ';\n')

                B_index = str(self.B_roots[np.int(j * self.B_roots_len / pow(2, i))] - 1)
                temp = 'B[' + B_index + ']'
                temp = self.boolian_and(temp, 'B_sign')
                file.write('assign ' + wire_temp_name_B + ' = ' + temp + ';\n')
            file.write('\n')
        file.write('\n')

    def make_A_B(self):
        # prepare A and B signal to produce PPs. These A and B supports all sign extensions which are needed for various fraction multipliers level 0 is the base line for each PP
        A = np.empty((self.B_chop_size + 1, self.A_chop_size + 1), dtype=object)
        for i in range(0, self.B_chop_size + 1):
            for j in range(0, self.A_chop_size + 1):
                if (j == self.A_chop_size):
                    A[i, j] = 'A_extended_level0_0'
                else:
                    A[i, j] = 'A[' + str(j) + ']'

        B = np.empty((self.B_chop_size + 1, self.A_chop_size + 1), dtype=object)
        for i in range(0, self.B_chop_size + 1):
            for j in range(0, self.A_chop_size + 1):
                if (i == self.B_chop_size):
                    B[i, j] = 'B_extended_level0_0'
                else:
                    B[i, j] = 'B[' + str(i) + ']'

        # affects of all other levels are added to A and B signals for each PP input
        for level in range(1, self.fraction_level + 1):
            for component_a in range(0, len(self.A_result[level])):
                for component_b in range(0, len(self.B_result[level])):

                    if (component_a == component_b):
                        # print('diagonal')
                        for i in range(0, self.B_result_mult_size[level] + 1):
                            for j in range(0, self.A_result_mult_size[level] + 1):
                                i_index = self.B_result[level][component_b] - i
                                j_index = self.A_result[level][component_a] - j
                                if ((i == 0) & (j == 0)):
                                    continue
                                elif (i == 0):
                                    B[i_index, j_index] = self.boolian_mux(B[i_index, j_index],
                                                                           'B_extended_level' + str(level) + '_' + str(
                                                                               component_b), 'HALF_' + str(level))
                                elif (j == 0):
                                    A[i_index, j_index] = self.boolian_mux(A[i_index, j_index],
                                                                           'A_extended_level' + str(level) + '_' + str(
                                                                               component_a), 'HALF_' + str(level))
                                else:
                                    continue
                    else:
                        # print('not diagonal')
                        continue
        return A, B

    def make_PP(self, A, B):
        # Prepare PPs
        # at first implement the PPs according to Level 0 as base line

        # prepare the extra Xor for changing the ANDs to NANDs
        XOR_controller = np.empty((self.B_chop_size + 1, self.A_chop_size + 1), dtype=object)
        for level in range(1, self.fraction_level + 1):
            for component_a in range(0, len(self.A_result[level])):
                for component_b in range(0, len(self.B_result[level])):

                    if (component_a == component_b):
                        # print('diagonal')
                        for i in range(0, self.B_result_mult_size[level] + 1):
                            for j in range(0, self.A_result_mult_size[level] + 1):
                                i_index = self.B_result[level][component_b] - i
                                j_index = self.A_result[level][component_a] - j

                                if ((i == 0) & (j == 0)):
                                    continue
                                elif ((i == 0) | (j == 0)):
                                    if (XOR_controller[i_index, j_index] == None):
                                        XOR_controller[i_index, j_index] = 'HALF_' + str(level)
                                    else:
                                        XOR_controller[i_index, j_index] = self.boolian_or(
                                            XOR_controller[i_index, j_index], 'HALF_' + str(level))
                                else:
                                    continue

        # Prepare AND NAND circuits for PPs regarding Xor part to control flexible AND--> NAND
        PP = np.empty((self.B_chop_size + 1, self.A_chop_size + 1), dtype=object)
        for i in range(0, self.B_chop_size + 1):
            for j in range(0, self.A_chop_size + 1):
                if ((i == self.B_chop_size) & (j == self.A_chop_size)):
                    PP[i, j] = self.boolian_and(A[i, j], B[i, j])
                elif (i == self.B_chop_size):
                    PP[i    , j] = self.boolian_nand(A[i, j], B[i, j])
                elif (j == self.A_chop_size):
                    PP[i, j] = self.boolian_nand(A[i, j], B[i, j])
                else:
                    PP[i, j] = self.boolian_and(A[i, j], B[i, j])
                    if (XOR_controller[i, j] != None):
                        PP[i, j] = self.boolian_xor(PP[i, j], XOR_controller[i, j])

        # Imply masking on each PP which should become zero just before addition
        for level in range(1, self.fraction_level + 1):
            for component_a in range(0, len(self.A_result[level])):
                for component_b in range(0, len(self.B_result[level])):

                    if (component_a == component_b):
                        # print('diagonal')
                        if ((component_a%2 == 1) | (component_b%2 == 1)):
                            if ((not(self.A_exception[level])) | (not(self.B_exception[level]))):     #$# it was AND. i changed it to OR
                                i_index = self.B_result[level][component_b]
                                j_index = self.A_result[level][component_a]
                                for iter in range(level, self.fraction_level + 1):
                                    PP[i_index, j_index] = self.boolian_masker(PP[i_index, j_index], 'HALF_' + str(iter))


                    elif (( ((component_a - component_b) == 1) & (component_a%2 == 1) ) | ( ((component_a - component_b) == -1) & (component_a%2 == 0) )):
                        # print('not diagonal - diff 1')

                        if (self.A_exception[level]):
                            if (component_a > component_b):
                                A_range_s = 1
                                A_range_f = self.A_result_mult_size[level] + 1
                            else:
                                A_range_s = 0
                                A_range_f = self.A_result_mult_size[level]
                        else:
                            A_range_s = 0
                            A_range_f = self.A_result_mult_size[level] + 1

                        if (self.B_exception[level]):
                            if (component_a > component_b):
                                B_range_s = 0
                                B_range_f = self.B_result_mult_size[level]
                            else:
                                B_range_s = 1
                                B_range_f = self.B_result_mult_size[level] + 1
                        else:
                            B_range_s = 0
                            B_range_f = self.B_result_mult_size[level] + 1

                        for i in range(B_range_s, B_range_f):
                            for j in range(A_range_s, A_range_f):
                                i_index = self.B_result[level][component_b] - i
                                j_index = self.A_result[level][component_a] - j

                                for iter in range(level, self.fraction_level + 1):
                                    PP[i_index, j_index] = self.boolian_masker(PP[i_index, j_index], 'HALF_' + str(iter))

                    else:
                        # print('not diagonal - diff more than 1')
                        continue

        return PP

    def writer_PP(self, file, PP):
        file.write('reg [A_chop_size:0] PP [B_chop_size:0];\n')
        file.write('always @(*) begin\n')
        for i in range(0, self.B_chop_size + 1):
            for j in range(0, self.A_chop_size + 1):
                file.write('\tPP[' + str(i) + '][' + str(j) + '] = ' + PP[i][j] + ';\n')
        file.write('end\n')
        file.write('\n')


    def make_Baugh_Wooley_strings(self):
        Extra_BW_1bit = np.empty((self.B_chop_size + self.A_chop_size + 1), dtype=object)
        Extra_BW_many_bits = np.empty((self.B_chop_size + self.A_chop_size + 1), dtype=object)
        for i in range(0, self.B_chop_size + self.A_chop_size + 1):
            Extra_BW_1bit[i] = '1\'b0'
            Extra_BW_many_bits[i] = '1\'b0'

        for level in range(0, self.fraction_level + 1):
            for component_a in range(0, len(self.A_result[level])):
                for component_b in range(0, len(self.B_result[level])):
                    if (component_a == component_b):
                        # print('diagonal')
                        i_index = self.B_result[level][component_b]
                        j_index = self.A_result[level][component_a]

                        temp_string = Extra_BW_1bit[i_index + j_index - (self.B_result_mult_size[level] - 1) - (
                        self.A_result_mult_size[level] - self.B_result_mult_size[level])]

                        temp_string = self.boolian_or('HALF_' + str(level), temp_string)

                        Extra_BW_1bit[i_index + j_index - (self.B_result_mult_size[level] - 1) - (
                                self.A_result_mult_size[level] - self.B_result_mult_size[level])] = temp_string

        for level in range(0, self.fraction_level + 1):
            for component_a in range(0, len(self.A_result[level])):
                for component_b in range(0, len(self.B_result[level])):
                    if (component_a == component_b):
                        # print('diagonal')
                        i_index = self.B_result[level][component_b]
                        j_index = self.A_result[level][component_a]
                        for iter in range(0, self.A_result_mult_size[level] - self.B_result_mult_size[level]):
                            temp_string = Extra_BW_many_bits[
                                i_index + j_index - (self.B_result_mult_size[level] + 1) - iter]
                            temp_string = self.boolian_or(temp_string, 'HALF_' + str(level))
                            Extra_BW_many_bits[
                                i_index + j_index - (self.B_result_mult_size[level] + 1) - iter] = temp_string

        # to compute the extra ones which are needed for Baugh-Wooley approach
        Extra_BW_1bit_string = ''
        Extra_BW_many_bits_string = ''
        for i in range(0, self.B_chop_size + self.A_chop_size + 1):
            if (i != 0):
                Extra_BW_many_bits_string = Extra_BW_many_bits_string + ','
                Extra_BW_1bit_string = Extra_BW_1bit_string + ','

            Extra_BW_many_bits_string = Extra_BW_many_bits_string + '{' + Extra_BW_many_bits[
                    self.B_chop_size + self.A_chop_size - i] + '}'
            Extra_BW_1bit_string = Extra_BW_1bit_string + '{' + Extra_BW_1bit[
                self.B_chop_size + self.A_chop_size - i] + '}'

        Extra_BW_many_bits_string = '{' + Extra_BW_many_bits_string + '}'
        Extra_BW_1bit_string = '{' + Extra_BW_1bit_string + '}'

        return Extra_BW_1bit_string, Extra_BW_many_bits_string

    def writer_PP_summations_new(self, file):
        # This method writes the summation circuits in the Verilog file

        # to get summation masks for each summation partial parts
        summation_mask_list = self.summation_mask_list_maker()

        # to calculate the extra 1 bits which are used for baugh-wooley multipliers
        # a string of zero and HALF_x signals
        # output is a string (concatenating string)
        Extra_BW_1bit_string, Extra_BW_many_bits_string = self.make_Baugh_Wooley_strings()

        # to calculate the dividing points in summation circuits regarding partial multipliers
        wall_points = self.wall_points_finder()

        # write on file a comment and define some integers
        file.write('// sum of PPs\n')
        file.write('integer j;\n')
        for wall_index in range(0, len(wall_points)):
            file.write('integer i_' + str(wall_index) + ';\n')
        file.write('\n')

        # write the baugh-wooley_0 extra bits in Verilog file
        file.write('wire [' + str(self.B_chop_size + self.A_chop_size) + ':0] Baugh_Wooley_0;\n')
        file.write('assign Baugh_Wooley_0 = ' + Extra_BW_1bit_string + ';\n')
        # to support both asymetric multipliers
        # write the baugh-wooley_1 extra bits in Verilog file
        file.write('wire [' + str(self.B_chop_size + self.A_chop_size) + ':0] Baugh_Wooley_1;\n')
        file.write('assign Baugh_Wooley_1 = ' + Extra_BW_many_bits_string + ';\n')
        file.write('\n')

        # reshape the PPs to PP_temp to have a rectangular shape of PPs in PP_temp
        # reshaping will change the parallelogram (AxB) to a rectangular ((A+B)x(B))
        file.write('reg [' + str(self.B_chop_size + self.A_chop_size) + ':0] PP_temp [' + str(self.B_chop_size ) + ':0];\n')
        file.write('always @(*) begin\n')
        file.write('\tfor (j = 0; j < (B_chop_size +1); j = j + 1 ) begin\n')
        file.write('\t\tPP_temp[j] = ' + str(self.B_chop_size + self.A_chop_size+1) + '\'b0 ;\n')
        file.write('\tend\n')
        file.write('\tfor (j = 0; j < (B_chop_size +1); j = j + 1 ) begin\n')
        file.write('\t\tPP_temp[j] = (PP[j] << j);\n')
        file.write('\tend\n')
        file.write('end\n')
        file.write('\n')


        C_temp_lenght = []
        C_temp_start = []
        C_temp_end = []
        # to compute C_temp start end and lenght
        for wall_index in range(0, len(wall_points)):
            if (wall_index == 0):
                wall_end = 0
            else:
                wall_end = wall_points[wall_index - 1]
            wall_start = wall_points[wall_index] - 1
            C_temp_lenght_temp = self.B_chop_size + self.A_chop_size - wall_end

            #C_temp_lenght.append(C_temp_lenght_temp + 1)
            C_temp_lenght.append(C_temp_lenght_temp)
            C_temp_start.append(wall_end)
            C_temp_end.append(wall_start)

        # creating the C_temp signals
        file.write('reg [' + str(C_temp_lenght[0] - 1) + ':0] C_temp_0;\n')
        file.write('reg [' + str(C_temp_lenght[0] - 1) + ':0] C_temp_1;\n')
        file.write('reg [' + str(C_temp_lenght[0] - 1) + ':0] C_0;\n')
        file.write('reg [' + str(C_temp_lenght[0] - 1) + ':0] C_1;\n')

        # write C_temp summation as for loops

        file.write('always @(*) begin\n')

        file.write('\tC_temp_1 [' + str(C_temp_end[0]) + ':0] = ' + str(C_temp_end[0] + 1) + '\'b0;\n')
        file.write('\tC_1 [' + str(C_temp_end[0]) + ':0] = C_temp_1 [' + str(C_temp_end[0]) + ':0];\n')

        turn = 0
        for index in range(0, len(wall_points)):

            PP_e = C_temp_end[index]
            if (index == 0):
                PP_s = 0
            else:
                PP_s = C_temp_end[index - 1] + 1

            PP_wall_string = '[' + str(PP_e) + ': ' + str(PP_s) + ']'

            C_temp_s = PP_s
            if (index == len(wall_points) - 1):
                C_temp_e = C_temp_end[index]
            else:
                C_temp_e = C_temp_end[index + 1]

            C_temp_string = '['+str(C_temp_e)+':'+str(C_temp_s)+']'

            temp_PP_string = ''
            for iter_temp in range(0, self.B_chop_size +1):
                if (iter_temp != 0):
                    temp_PP_string = temp_PP_string + ' + '
                temp_PP_string = temp_PP_string + 'PP_temp[' + str(iter_temp) + ']' + PP_wall_string

            temp_PP_string = temp_PP_string + ' + Baugh_Wooley_0' + PP_wall_string + ' + Baugh_Wooley_1' + PP_wall_string;
            file.write('\tC_temp_' + str(turn) + C_temp_string + ' = ' + temp_PP_string + ';\n')

            temp_mask = '{{' + str(C_temp_e - PP_e) + '{'+ self.arch_masker[index] +'}},{'+str(PP_e - PP_s + 1)+'{1\'b0}}}'
            temp_new_c_i = self.boolian_masker('C_temp_'+str(turn) + C_temp_string, temp_mask)
            file.write('\tC_' + str(turn) + C_temp_string + ' = ' + temp_new_c_i + ';\n')

            # to change turn
            turn = (turn + 1) % 2


        file.write('end\n')
        file.write('\n')

        #Make_carry_look_a_head_string
        for index in range(0, len(wall_points)-1):
            file.write('reg C_carry_temp_' + str(index) + ';\n')

        file.write('reg signed [A_chop_size+B_chop_size-1:0] C_temp;\n')
        file.write('always @(*) begin\n')

        if (self.parameter_optimization_carry_look_ahead):

            for index in range(0, len(wall_points)):
                PP_e = C_temp_end[index]
                if (index == 0):
                    PP_s = 0
                else:
                    PP_s = C_temp_end[index - 1] + 1

                PP_wall_string = '[' + str(PP_e) + ': ' + str(PP_s) + ']'

                result_s = 'C_temp' + PP_wall_string

                oprand_s = 'C_0'+PP_wall_string+' + C_1' + PP_wall_string
                if (index != 0):
                    carry_s = self.boolian_masker('C_carry_temp_' + str(index - 1), self.arch_masker[index-1]);
                    carry_s = '(' + carry_s + ')'
                    oprand_s = oprand_s + ' + ' + carry_s

                temp_s = result_s + ' = ' + oprand_s + ';'
                file.write('\t' + temp_s + '\n')


                if (index != len(wall_points)-1):
                    if (index == 0):
                        carry_look_ahead = 'C_carry_temp_' + str(index) + ' = ' + self.Make_carry_look_a_head_string('C_0', 'C_1', PP_s, PP_e, '(1\'b0)') + ';'
                    else:
                        carry_look_ahead = 'C_carry_temp_' + str(index) + ' = ' + self.Make_carry_look_a_head_string('C_0', 'C_1', PP_s, PP_e, 'C_carry_temp_' + str(index-1)) + ';'

                    file.write('\t' + carry_look_ahead + '\n')
        else:

            for index in range(0, len(wall_points)):
                PP_e = C_temp_end[index]
                if (index == 0):
                    PP_s = 0
                else:
                    PP_s = C_temp_end[index - 1] + 1

                PP_wall_string = '[' + str(PP_e) + ': ' + str(PP_s) + ']'

                result_s = 'C_temp' + PP_wall_string
                if (index != len(wall_points) - 1):
                    result_s = '{{C_carry_temp_' + str(index) + '}, {' + result_s + '}}'
                oprand_s = 'C_0' + PP_wall_string + ' + C_1' + PP_wall_string
                if (index != 0):
                    carry_s = self.boolian_masker('C_carry_temp_' + str(index - 1), self.arch_masker[index - 1]);
                    carry_s = '(' + carry_s + ')'
                    oprand_s = oprand_s + ' + ' + carry_s

                temp_s = result_s + ' = ' + oprand_s + ';'
                file.write('\t' + temp_s + '\n')


        file.write('end\n')

        if (self.parameter_optimization_pipeline):
            file.write('always @ (posedge clk) begin\n')
            file.write('\tif(reset)\n')
            file.write('\t\tC <= 0;\n')
            file.write('\telse\n')
            file.write('\t\tC <= C_temp[A_chop_size+B_chop_size-1:0];\n')
            file.write('end\n')
        else:
            file.write('always @ (*) begin\n')
            file.write('\t\tC = C_temp[A_chop_size+B_chop_size-1:0];\n')
            file.write('end\n')

        file.write('\n')




    def summation_mask_list_maker(self):
        # Prepare a mask for summation part to mask upper bits

        # Create an array of None
        summation_mask_list = np.empty(pow(2, self.fraction_level), dtype=object)

        # Example: loop over the levels and make the special pattern
        # output for 2-level multiplier:
        #           summation_mask_list = [HALF_2, (HALF_2 | HALF_1), HALF_2, (HALF_2 | HALF_1 | HALF_0)]
        # output for 1-level multiplier:
        #           summation_mask_list = [HALF_1, (HALF_1 | HALF_0)]
        for level in range(0, self.fraction_level+1):
            for index in range(pow(2, self.fraction_level - level) - 1, len(summation_mask_list),
                               pow(2, self.fraction_level - level)):
                if (summation_mask_list[index] == None):
                    summation_mask_list[index] = 'HALF_' + str(level)
                else:
                    summation_mask_list[index] = self.boolian_or(summation_mask_list[index], 'HALF_' + str(level))

        return summation_mask_list

    def writer_end_module(self, file):
        # This method writes the ending string in a Verilog file
        file.write('\n')
        file.write('endmodule\n')

    def writer_timescale_and_module_name(self, file, module_name, closed):
        # Writes the time scale and module name on top of Verilog file
        file.write('`timescale 1 ns / 100 ps  \n')
        if (closed):
            file.write('module ' + module_name + '();\n')
        else:
            file.write('module ' + module_name + '(\n')

    def writer_clock_generator(self, file):
        # writes clock generator code for test bench 100MHz
        file.write('reg clk;\n')
        file.write('initial begin\n')
        file.write('\tclk = 0;\n')
        file.write('\tforever #5 clk= ~clk;\n')
        file.write('end\n\n')

    def module_name_generator(self, module_name):

        temp_chop_size = 'C' + str(self.A_chop_number) + 'x' + str(self.B_chop_number) + '_'
        temp_fracture_size = 'F' + str(self.fraction_level) + '_'

        if module_name == 'top':
            temp_A = str(self.A_width) + 'bits_'
            temp_B = str(self.B_width) + 'bits_'
            return 'multiplier_T_' + temp_chop_size + temp_fracture_size + temp_A + temp_B + 'HighLevelDescribed_auto'
        elif module_name == 'sub':
            temp_A = str(self.A_chop_size) + 'bits_'
            temp_B = str(self.B_chop_size) + 'bits_'
            return 'multiplier_S_' + temp_chop_size + temp_fracture_size + temp_A + temp_B + 'HighLevelDescribed_auto'

        elif module_name == 'alu_s':
            return 'ALU_SIMD_Width_parameterized_HighLevelDescribed_auto'

        elif module_name == 'alu_s_tb':
            return 'ALU_SIMD_Width_parameterized_HighLevelDescribed_auto_tb'

        elif module_name == 'alu_t':
            temp_A = str(self.A_width) + 'bits_'
            temp_B = str(self.B_width) + 'bits_'
            return 'ALU_T_' + temp_chop_size + temp_fracture_size + temp_A + temp_B + 'HighLevelDescribed_auto'

        else:
            raise NameError('$$ Error: in \'module_name_generator\'')

    def Make_model_files_chopped(self):
        # This method writes the chopped multiplier module as a .v file

        # module name and file name
        # module and tester name
        module_name = self.module_name_generator('sub')

        # open the .v file to write
        file = open(self.output_directory + module_name + '.v', 'w')

        # writing time scale and module name in the file
        self.writer_timescale_and_module_name(file, module_name, 0)

        # writing the module inputs regarding the widths
        self.writer_module_chopped_input(file)

        # preparing the signed extension signals by input A and B
        self.writer_input_sign_extended(file)

        if ((self.fraction_level == 0) and (self.parameter_optimization_F0)):
            file.write('reg signed [A_chop_size+B_chop_size+1:0] C_temp;\n')
            file.write('always @ (*) begin\n')
            file.write('\t C_temp = $signed({{A_extended_level0_0},{A}}) * $signed({{B_extended_level0_0},{B}});\n')
            file.write('end\n')
            file.write('\n')
            file.write('always @ (posedge clk) begin\n')
            file.write('\tif(reset)\n')
            file.write('\t\tC <= 0;\n')
            file.write('\telse\n')
            file.write('\t\tC <= C_temp[A_chop_size+B_chop_size-1:0];\n')
            file.write('end\n')
        else:
            # using input A, B, signed extension signals to prepare A[i, j] and B[i, j] for each PPs
            # the outputs are matrix A and B which are included the boolean function of inputs for AND/NAND gate of each PPs
            A, B = self.make_A_B()

            # making PPs regarding location and computation mode
            # masking circuits and negating circuits by XOR is implemented
            PP = self.make_PP(A, B)

            # writing the PPs in Verilog file
            self.writer_PP(file, PP)

            # writing the summation circuits in the Verilog file
            self.writer_PP_summations_new(file)

        # writing the end of Verilog file (endmodule)
        self.writer_end_module(file)

        # closing the file
        file.close()

    def Make_carry_look_a_head_string(self, A_s, B_s, ind_s, ind_e, cin_s):
        N = ind_e - ind_s + 1
        logic = '('

        for n in range(N-1, -2, -1):
            for index in range(N - 1, n, -1):
                P_string = '((' + A_s + '[' + str(index + ind_s) + '])^(' + B_s + '[' + str(index + ind_s)+']))&'
                #P_string = 'P' + str(index+ind_s) + '&'
                logic = logic + P_string

            if (n !=  -1):
                G_string = '((' + A_s + '[' + str(n + ind_s) + '])&(' + B_s + '[' + str(n + ind_s) + ']))'
                #G_string = 'G' + str(n+ind_s)
                logic = logic + G_string + ')|('
            else:
                Cin_string = cin_s + ')'
                #Cin_string = 'Cin' + ')'
                logic = logic + Cin_string

        logic = '(' + logic + ')'
        return logic


    def Make_model_files_chopped_tb(self):
        # This module prepare a test bench for chopped multiplier

        # module and tester name
        module_name = self.module_name_generator('sub')
        module_tester_name = module_name + '_tb'

        # open the .v file to write
        file = open(self.output_directory + module_tester_name + '.v', 'w')

        # writing time scale and module name in the file
        self.writer_timescale_and_module_name(file, module_tester_name, 1)
        file.write('\n')
        # write parameters and signals and wires
        # parameters
        file.write('parameter A_chop_size = ' + str(self.A_chop_size) + ';\n')
        file.write('parameter B_chop_size = ' + str(self.B_chop_size) + ';\n')
        file.write('parameter test_max_counter = ' + str(self.test_max_counter) + ';\n')
        file.write('\n')

        #integers
        file.write('integer counter, Error_counter;\n')
        file.write('\n')

        # regs
        file.write('reg signed [A_chop_size - 1:0]  A;\n')
        file.write('reg signed [B_chop_size - 1:0]  B;\n')
        file.write('\n')
        file.write('reg A_sign;\n')
        file.write('reg B_sign;\n')
        file.write('\n')
        for level in range(0, self.fraction_level + 1):
            file.write('reg  HALF_' + str(level) + ';\n')
        file.write('\n')

        # wires
        file.write('wire signed [' + str(self.A_chop_size + self.B_chop_size - 1) + ':0] C;\n')
        #file.write('wire signed [' + str(self.A_chop_size + self.B_chop_size - 1) + ':0] C_0;\n')
        #file.write('wire signed [' + str(self.A_chop_size + self.B_chop_size - 1) + ':0] C_1;\n')
        file.write('\n')

        # writes the clock generator code for test bench
        self.writer_clock_generator(file)

        file.write('initial begin\n')
        file.write('\tError_counter = 0;\n')
        file.write('\t@(posedge clk);\n')
        file.write('\t@(posedge clk);\n')
        file.write('\n')

        for level in range(0, self.fraction_level + 1):
            for signed in range(0, 2):  #0/1 --> unsigned/signed

                if signed:
                    unsigned_string = ''
                else:
                    unsigned_string = 'un'
                file.write(
                    '\t// check ' + unsigned_string + 'signed mult ' + str(self.A_result_mult_size[level]) + 'x' + str(
                        self.B_result_mult_size[level]) + '\n')
                file.write('\tfor (counter = 0; counter < test_max_counter; counter = counter + 1) begin \n')
                file.write('\t\tA = $random;\n')
                file.write('\t\tB = $random;\n')
                file.write('\n')
                file.write('\t\tA_sign = 1\'b' + str(signed) + ';\n')
                file.write('\t\tB_sign = 1\'b' + str(signed) + ';\n')
                file.write('\n')

                for level_temp in range(0, self.fraction_level + 1):
                    if (level_temp == level):
                        one_hot = 1
                    else:
                        one_hot = 0
                    file.write('\t\tHALF_'+str(level_temp)+' = 1\'b'+str(one_hot)+ ';\n')

                file.write('\n')
                file.write('\t\t@(posedge clk);\n')
                file.write('\t\t#1\n')

                for index in range(0, pow(2, level)):
                    A_string = '$' + unsigned_string + 'signed(A[' + str(self.A_result[level][index] - 1) + ':' + str(
                        self.A_result[level][index] - self.A_result_mult_size[level]) + '])'
                    B_string = '$' + unsigned_string + 'signed(B[' + str(self.B_result[level][index] - 1) + ':' + str(
                        self.B_result[level][index] - self.B_result_mult_size[level]) + '])'
                    C_string = '$' + unsigned_string + 'signed(C[' + str(
                        self.A_result[level][index] + self.B_result[level][index] - 1) + ':' + str(
                        self.A_result[level][index] + self.B_result[level][index] - self.A_result_mult_size[level] -
                        self.B_result_mult_size[level]) + '])'
                    #C_string = '$' + unsigned_string + 'signed(C_0[' + str(
                    #    self.A_result[level][index] + self.B_result[level][index] - 1) + ':' + str(
                    #    self.A_result[level][index] + self.B_result[level][index] - self.A_result_mult_size[level] -
                    #    self.B_result_mult_size[level]) + ']+ C_1[' + str(
                    #    self.A_result[level][index] + self.B_result[level][index] - 1) + ':' + str(
                    #    self.A_result[level][index] + self.B_result[level][index] - self.A_result_mult_size[level] -
                    #    self.B_result_mult_size[level]) + '])'

                    if (index == 0):
                        condition_string = '(' + A_string + ' * ' + B_string + ' != ' + C_string + ')'
                    else:
                        condition_string = condition_string + '||' + '(' + A_string + ' * ' + B_string + ' != ' + C_string + ')'

                condition_string = '('+condition_string+')'

                file.write('\t\tif  ' + condition_string + ' begin\n')
                for index in range(0, pow(2, level)):
                    A_string = '$' + unsigned_string + 'signed(A[' + str(self.A_result[level][index] - 1) + ':' + str(
                        self.A_result[level][index] - self.A_result_mult_size[level]) + '])'
                    B_string = '$' + unsigned_string + 'signed(B[' + str(self.B_result[level][index] - 1) + ':' + str(
                        self.B_result[level][index] - self.B_result_mult_size[level]) + '])'
                    C_string = '$' + unsigned_string + 'signed(C[' + str(
                        self.A_result[level][index] + self.B_result[level][index] - 1) + ':' + str(
                        self.A_result[level][index] + self.B_result[level][index] - self.A_result_mult_size[level] -
                        self.B_result_mult_size[level]) + '])'
                    #C_string = '$' + unsigned_string + 'signed(C_0[' + str(
                    #    self.A_result[level][index] + self.B_result[level][index] - 1) + ':' + str(
                    #    self.A_result[level][index] + self.B_result[level][index] - self.A_result_mult_size[level] -
                    #    self.B_result_mult_size[level]) + ']+ C_1[' + str(
                    #    self.A_result[level][index] + self.B_result[level][index] - 1) + ':' + str(
                    #    self.A_result[level][index] + self.B_result[level][index] - self.A_result_mult_size[level] -
                    #    self.B_result_mult_size[level]) + '])'
                    file.write('\t\t\t$display("Error: \tA' + str(index) + ' = %b, B' + str(index) + ' = %b, C' + str(
                        index) + ' = %b", ' + A_string + ', ' + B_string + ', ' + C_string + ');\n')
                file.write('\t\t\tError_counter = Error_counter + 1;\n')
                file.write('\t\tend\n')

                file.write('\tend\n')
                file.write('\n')
                file.write('\n')


        # reporting the error counter
        file.write('\n')
        file.write('\t$display(" ");\n')
        file.write('\tif (Error_counter != 0)begin\n')
        file.write('\t\t$display("--> Error: there was %d wrong answer", Error_counter);\n')
        file.write('\tend else begin\n')
        file.write('\t\t$display("--> Correct: there was no wrong answer :) ");\n')
        file.write('\tend\n')
        file.write('\t$display(" ");\n')
        file.write('\n')
        file.write('\n')

        # finishing the simulation
        file.write('\n')
        file.write('\t@(posedge clk);\n')
        file.write('\t@(posedge clk);\n')
        file.write('\t$finish();\n')
        file.write('end\n')
        file.write('\n')

        # instantiate the module
        file.write( module_name + '\t' + module_name + '_inst(\n')
        file.write('\t.A(A),\n')
        file.write('\t.B(B),\n')
        file.write('\n')
        file.write('\t.A_sign(A_sign),\n')
        file.write('\t.B_sign(B_sign),\n')
        file.write('\n')
        for level in range(0, self.fraction_level + 1):
            file.write('\t.HALF_' + str(level) + '(HALF_' + str(level) + '),\n')
        file.write('\n')
        file.write('\t.C(C)\n')
        #file.write('\t.C_0(C_0),\n')
        #file.write('\t.C_1(C_1)\n')
        file.write(');\n')

        # writing the end of Verilog file (endmodule)
        self.writer_end_module(file)

        # closing the file
        file.close()

    def writer_module_top_input_parameters_signals(self, file):
        # writes the inputs of top module

        # inputs
        file.write('\t\tinput clk,\n')
        file.write('\t\tinput reset,\n')
        file.write('\t\t\n')
        file.write('\t\tinput [' + str((self.T_chop_number * self.A_chop_size) - 1) + ':0] a,\n')
        file.write('\t\tinput [' + str((self.T_chop_number * self.B_chop_size) - 1) + ':0] b,\n')
        file.write('\t\t\n')

        file.write('\t\tinput a_sign,\n')
        file.write('\t\tinput b_sign,\n')
        file.write('\t\t\n')

        mode_counter, mode_counter_log, mode_strings = self.writer_parameter_modes(file, False)

        file.write('\t\tinput [' + str(mode_counter_log-1) + ':0] mode,\n')
        file.write('\t\t\n')

        # outputs
        file.write('\t\toutput reg [' + str(self.A_width + self.B_width - 1) + ':0] result_0,\n')
        file.write('\t\toutput reg [' + str(self.A_width + self.B_width - 1) + ':0] result_1,\n')
        file.write('\t\toutput reg [' + str(self.arch_Saving_precision_SE_size * len(self.arch_splitters) - 1) + ':0] result_SIMD_carry\n')
        file.write('\t);\n')
        file.write('\n')

        file.write('\t\treg [' + str((self.T_chop_number * self.A_chop_size) - 1) + ':0] a_reg;\n')
        file.write('\t\treg [' + str((self.T_chop_number * self.B_chop_size) - 1) + ':0] b_reg;\n')
        file.write('\t\treg a_sign_reg;\n')
        file.write('\t\treg b_sign_reg;\n')
        file.write('always @ (posedge clk) begin\n')
        file.write('\tif (reset) begin\n')
        file.write('\t\ta_reg <= 0;\n')
        file.write('\t\tb_reg <= 0;\n')
        file.write('\t\ta_sign_reg <= 0;\n')
        file.write('\t\tb_sign_reg <= 0;\n')
        file.write('\tend\n')
        file.write('\telse begin \n')
        file.write('\t\ta_reg <= a;\n')
        file.write('\t\tb_reg <= b;\n')
        file.write('\t\ta_sign_reg <= a_sign;\n')
        file.write('\t\tb_sign_reg <= b_sign;\n')
        file.write('\tend\n')
        file.write('end\n')
        file.write('\n')

        mode_counter, mode_counter_log, mode_strings = self.writer_parameter_modes(file, True)

        # create HALF signals
        file.write('// internal signal for half mode detection\n')
        for level in range(0, self.fraction_level + 1):
            file.write('wire HALF_' + str(level) + ';\n')
        file.write('\n')

        file.write('// input of partial multipliers\n')
        for i in range(0, self.T_chop_number):
            file.write('reg [' + str(self.A_chop_size - 1) + ':0] A_' + str(i) + ';\n')
        file.write('\n')

        for i in range(0, self.T_chop_number):
            file.write('reg [' + str(self.B_chop_size - 1) + ':0] B_' + str(i) + ';\n')
        file.write('\n')

        for i in range(0, self.T_chop_number ):
            file.write('wire [' + str(self.A_chop_size + self.B_chop_size - 1) + ':0] C_' + str(i) + ';\n')
        file.write('\n')

        for i in range(0, self.T_chop_number ):
            file.write('reg A_sign_' + str(i) + ';\n')
        file.write('\n')

        for i in range(0, self.T_chop_number ):
            file.write('reg B_sign_' + str(i) + ';\n')
        file.write('\n')

        return mode_strings, mode_counter


    def writer_module_top_instanciate(self, file, mode_strings, mode_counter):
        file.write('// to assign the input to sub multipliers \n')
        file.write('always @(*) begin\n')
        file.write('\tcase (mode_SIMD)\n')
        file.write('\t\t1\'b0: begin\n')
        for i in range(0, self.B_chop_number):
            for j in range(0, self.A_chop_number):
                index = self.arch[i][j]
                file.write('\t\t\tA_' + str(index) + ' = a_reg[' + str((j + 1) * (self.A_chop_size) - 1) + ':' + str(
                    (j) * self.A_chop_size) + '];\n')
        file.write('\n')
        for i in range(0, self.B_chop_number):
            for j in range(0, self.A_chop_number):
                index = self.arch[i][j]
                file.write('\t\t\tB_' + str(index) + ' = b_reg[' + str((i + 1) * (self.B_chop_size) - 1) + ':' + str(
                    (i) * self.B_chop_size) + '];\n')
        file.write('\t\tend\n')
        file.write('\t\t1\'b1: begin\n')
        for i in range(0, self.B_chop_number):
            for j in range(0, self.A_chop_number):
                index = self.arch[i][j]
                file.write('\t\t\tA_' + str(index) + ' = a_reg[' + str((index + 1) * (self.A_chop_size) - 1) + ':' + str(
                    (index) * self.A_chop_size) + '];\n')
        file.write('\n')
        for i in range(0, self.B_chop_number):
            for j in range(0, self.A_chop_number):
                index = self.arch[i][j]
                file.write('\t\t\tB_' + str(index) + ' = b_reg[' + str((index + 1) * (self.B_chop_size) - 1) + ':' + str(
                    (index) * self.B_chop_size) + '];\n')
        file.write('\t\tend\n')
        file.write('\tendcase\n')
        file.write('end\n\n')

        file.write('//sign controller\n')
        file.write('reg mode_SIMD;\n')
        file.write('always @(*) begin\n')
        file.write('\tcase (mode)\n')

        file.write('\t\t' +mode_strings[0]+ ': begin\n')
        file.write('\t\t\tmode_SIMD = 1\'b0;\n')
        for i in range(0, self.B_chop_number):
            for j in range(0, self.A_chop_number):
                index = self.arch[i][j]
                if (j == (self.A_chop_number - 1)):
                    file.write('\t\t\tA_sign_' + str(index) + ' = a_sign_reg;\n')
                else:
                    file.write('\t\t\tA_sign_' + str(index) + ' = 1\'b0;\n')

        file.write('\n')
        for i in range(0, self.B_chop_number):
            for j in range(0, self.A_chop_number):
                index = self.arch[i][j]
                if (i == (self.B_chop_number - 1)):
                    file.write('\t\t\tB_sign_' + str(index) + ' = b_sign_reg;\n')
                else:
                    file.write('\t\t\tB_sign_' + str(index) + ' = 1\'b0;\n')

        file.write('\t\tend\n')
        file.write('\t\tdefault: begin\n')
        file.write('\t\t\tmode_SIMD = 1\'b1;\n')
        for i in range(0, self.B_chop_number):
            for j in range(0, self.A_chop_number):
                index = self.arch[i][j]
                file.write('\t\t\tA_sign_' + str(index) + ' = a_sign_reg;\n')
        file.write('\n')
        for i in range(0, self.B_chop_number):
            for j in range(0, self.A_chop_number):
                index = self.arch[i][j]
                file.write('\t\t\tB_sign_' + str(index) + ' = b_sign_reg;\n')
        file.write('\t\tend\n')

        file.write('\tendcase\n')
        file.write('end\n\n')

        # assign HALF signals
        file.write('// Assigning half mode signals\n')
        file.write('assign FULL = (mode == ' + mode_strings[0] + ');\n')
        for level in range(0, self.fraction_level + 1):
            file.write('assign HALF_' + str(level) + ' = (mode == ' + mode_strings[level + 1] + ');\n')
        file.write('\n')

        # it means the names which are looking to generate is not top module names and are submodule names

        for i in range(0, self.T_chop_number):
            temp_module_name = self.module_name_generator('sub')
            file.write(temp_module_name + '\t\t' + temp_module_name + '_inst' + str(i) + '(\n')
            if (self.parameter_optimization_pipeline):
                file.write('\t.clk(clk),\n')
                file.write('\t.reset(reset),\n')
                file.write('\n')
            file.write('\t.A(A_' + str(i) + '),\n')
            file.write('\t.B(B_' + str(i) + '),\n')
            file.write('\n')
            file.write('\t.A_sign(A_sign_' + str(i) + '),\n')
            file.write('\t.B_sign(B_sign_' + str(i) + '),\n')
            file.write('\n')
            for level in range(0, self.fraction_level + 1):
                if (level == 0):
                    file.write('\t.HALF_0(HALF_0 | FULL),\n')
                else:
                    file.write('\t.HALF_' + str(level) + '(HALF_' + str(level) + '),\n')
            file.write('\n')
            file.write('\t.C(C_' + str(i) + ')\n')
            file.write(');\n\n')

        file.write('\n')

    def shifter(self, input, A_j, B_i, width_step, partial, sign_signal, SIMD):
        width_total   = self.A_width + self.B_width
        width_input   = self.A_chop_size + self.B_chop_size
        width_prefix  = (A_j * self.A_chop_size) + (B_i * self.B_chop_size)
        width_postfix = width_total- width_prefix - width_input

        if (not(SIMD)):
            prefix_string = ''
            if (width_prefix != 0):
                prefix_string = ', {' + str(width_prefix) + '{1\'b0}}'

            postfix_string = ''
            if (width_postfix != 0):
                postfix_string = input + '[' + str(self.A_chop_size + self.B_chop_size - 1) + ']'
                postfix_string = self.boolian_and(postfix_string, sign_signal)

                postfix_string = '{' + str(width_postfix) + '{' + postfix_string + '}}, '

            output_string_normal = '{' + postfix_string +  '{' + input + '}' + prefix_string + '}'

            return output_string_normal

        else:
            if (width_step > 0):
                width_postfix = width_postfix - width_step
            elif (width_step < 0):
                width_prefix = width_prefix - (-width_step)

            prefix_string = ''
            if (width_prefix > 0):
                prefix_string = ', {'+str(width_prefix)+'{1\'b0}}'

            postfix_string = ''
            if (width_postfix > 0):
                postfix_string = '{'+str(width_postfix)+'{1\'b0}}, '

            output_string_SIMD = '{' + input + '}'

            if (width_step > 0):
                if (partial):
                    partial_string = ', {'+ input +'['+str(width_step-1)+':0]}'
                    output_string_SIMD = output_string_SIMD + partial_string
                else:
                    partial_string = ', {' + str(width_step) + '{1\'b0}}'
                    output_string_SIMD = output_string_SIMD + partial_string
            elif (width_step < 0):
                partial_string = '{' + str(-width_step) + '{1\'b0}} ,'
                output_string_SIMD = partial_string + output_string_SIMD

            output_string_SIMD = '{' + postfix_string + output_string_SIMD  + prefix_string + '}'

            return output_string_SIMD

    def writer_module_top_shifter_summation(self, file):
        # this module writes the shifter and summation section of top module
        file.write('// to implement shifters for SIMD modes\n')

        for i in range(0, self.T_chop_number):
            file.write('reg [' + str(self.A_width + self.B_width-1) + ':0] C_' + str(i) + '_shifted;\n')

        file.write('always @ (*) begin\n')
        file.write('\tcase (mode_SIMD)\n')

        file.write('\t\t1\'b0: begin\n')
        for i in range(0, self.B_chop_number):
            for j in range(0, self.A_chop_number):
                index = self.arch[i][j]
                temp_sign = self.boolian_or('A_sign_' + str(index), 'B_sign_' + str(index))
                temp_C = 'C_' + str(index)
                temp_step = self.arch_shift[i][j]
                #$# i,j ==chaged to ==> j,i
                file.write(
                    '\t\t\tC_' + str(index) + '_shifted = ' + self.shifter(temp_C, j, i, temp_step, (i == 0) & (j == 0),
                                                                           temp_sign, 0) + ';\n')
        file.write('\t\tend\n')

        file.write('\t\t1\'b1: begin\n')
        for i in range(0, self.B_chop_number):
            for j in range(0, self.A_chop_number):
                index = self.arch[i][j]
                temp_sign = self.boolian_or('A_sign_' + str(index), 'B_sign_' + str(index))
                temp_C = 'C_' + str(index)
                temp_step = self.arch_shift[i][j]
                # $# i,j ==chaged to ==> j,i
                file.write(
                    '\t\t\tC_' + str(index) + '_shifted = ' + self.shifter(temp_C, j, i, temp_step, (i == 0) & (j == 0),
                                                                           temp_sign, 1) + ';\n')
        file.write('\t\tend\n')
        file.write('\tendcase\n')
        file.write('end\n\n')



        if (self.parameter_optimization_parallelism_T == 1):
            arch_splitters_selected = self.arch_splitters_maxFraction
            arch_masker_selected = self.arch_masker_maxFraction
        else:
            arch_splitters_selected = self.arch_splitters
            arch_masker_selected = self.arch_masker


        file.write('// to assign output pairs \n')
        file.write('reg [' + str(self.A_width + self.B_width - 1) + ':0] result_temp_0;\n')
        file.write('reg [' + str(self.A_width + self.B_width + self.arch_Saving_precision_SE_size - 1) + ':0] result_temp_1;\n')

        file.write('always @ (*) begin\n')

        file.write('\tresult_temp_1 [' + str(arch_splitters_selected[0]) + ':0] = ' + str(
            arch_splitters_selected[0] + 1) + '\'b0;\n')
        file.write('\tresult_1 [' + str(arch_splitters_selected[0]) + ':0] = result_temp_1 [' + str(
            str(arch_splitters_selected[0])) + ':0];\n')

        turn = 0
        for index in range(0, len(arch_splitters_selected)):
            # end and start for "C_i"
            wall_end = arch_splitters_selected[index]
            if (index == 0):
                wall_start = 0
            else:
                wall_start = arch_splitters_selected[index - 1] + 1

            # end and start for "result_temp_i"
            result_temp_wall_start = wall_start
            if (index == len(arch_splitters_selected) - 1):
                result_temp_wall_end = arch_splitters_selected[index] + self.arch_Saving_precision_SE_size
            else:
                result_temp_wall_end =  arch_splitters_selected[index + 1]

            # end and start for "result_i"
            result_wall_start = wall_start
            if (index == len(arch_splitters_selected) - 1):
                result_wall_end = arch_splitters_selected[index]
            else:
                result_wall_end = arch_splitters_selected[index + 1]

            result_temp_s = 'result_temp_' + str(turn) + ' [' + str(result_temp_wall_end) + ':' + str(
                result_temp_wall_start) + ']'
            result_temp_s_main = 'result_temp_' + str(turn) + ' [' + str(wall_end) + ':' + str(
                result_temp_wall_start) + ']'
            result_temp_string_maskable = 'result_temp_' + str(turn) + ' [' + str(result_temp_wall_end) + ':' + str(
                wall_end+1) + ']'
            masker_string = '{'+str(result_temp_wall_end-wall_end) +'{'+arch_masker_selected[index]+'}}'

            masked_string = self.boolian_masker(result_temp_string_maskable, masker_string)

            result_string = 'result_' + str(turn) + ' [' + str(result_wall_end) + ':' + str(result_wall_start) + ']'


            temp_ind_s = '[' + str(wall_end) + ':' + str(wall_start) + ']'
            for ii in range(0, self.T_chop_number):
                temp_part_s = 'C_' + str(ii) + '_shifted ' + temp_ind_s

                if (arch_masker_selected[index] != ''):
                    temp_sign_extended_s = 'C_'+str(ii)+'_shifted[' + str(wall_end) + ']'
                    temp_sign_extended_s = self.boolian_and(temp_sign_extended_s, arch_masker_selected[index])
                    temp_sign_extended_s = self.boolian_and(temp_sign_extended_s, '(a_sign|b_sign)')
                    temp_part_s = '{{' + str(self.arch_Saving_precision_SE_size) + '{'+temp_sign_extended_s+'}},{' + temp_part_s + '}}'

                if (ii == 0):
                    temp_total_s = temp_part_s
                else:
                    temp_total_s = temp_total_s + ' + ' + temp_part_s



            file.write('\t' + result_temp_s + ' = ' + temp_total_s + ';\n')

            if (index == len(arch_splitters_selected) - 1):
                file.write('\t' + result_string + ' = ' + result_temp_s_main + ';\n')
            elif(arch_masker_selected[index] == ''):
                file.write('\t' + result_string + ' = ' + result_temp_s + ';\n')
            else:
                file.write('\t' + result_string + ' = {{' + masked_string + '},{' + result_temp_s_main + '}};\n')

            if (self.arch_masker_maxFraction[index] != ''):
                index_new = int(index/(pow(2,self.fraction_level_maxFraction-self.fraction_level)))
                temp_SE_carry_in_temp_s = 'result_temp_' + str(turn) + ' [' + str(
                    wall_end + self.arch_Saving_precision_SE_size) + ':' + str(wall_end + 1) + ']'
                temp_SE_carry_s = 'result_SIMD_carry[' + str(
                    self.arch_Saving_precision_SE_size * (index_new + 1) - 1) + ':' + str(
                    self.arch_Saving_precision_SE_size * index_new) + ']'

                file.write('\t' + temp_SE_carry_s + ' = ' + temp_SE_carry_in_temp_s + ';\n')

            # to change turn
            turn = (turn + 1) % 2

        file.write('end\n')


    def Make_model_files_top(self):

        # This method writes the chopped multiplier module as a .v file
        # module name and file name
        # module and tester name
        module_name = self.module_name_generator('top')

        # open the .v file to write
        file = open(self.output_directory + module_name + '.v', 'w')

        # writing time scale and module name in the file
        self.writer_timescale_and_module_name(file, module_name, 0)

        # writing the module inputs regarding the widths
        mode_strings, mode_counter = self.writer_module_top_input_parameters_signals(file)

        self.writer_module_top_instanciate(file, mode_strings, mode_counter)

        self.writer_module_top_shifter_summation(file)
        file.write('\n')

        # writing the end of Verilog file (endmodule) & closing the file
        self.writer_end_module(file)

        file.close()

    def writer_head_line(self, file, string):
        file.write('/*******************************************************\n')
        file.write('*\t' + string + '\n')
        file.write('*******************************************************/\n')

    def writer_parameter_modes(self, file, write_enable):
        # mode signals
        temp = len(self.supported_multipliers_list)
        mode_counter = 0
        if (temp == 2):
            mode_counter = 1 + len(self.supported_multipliers_list[1])
            mode_counter_log = np.int(np.ceil(np.log2(mode_counter)))
        else:
            raise NameError(
                '$$ Error: there is a problem with supported multiplier list we look for a 2-element array which the second element is a array')

        if (write_enable):
            file.write('// functionality modes \n')
        mode_strings = []
        mode_strings_temp = 'mode_' + str(self.supported_multipliers_list[0][0]) + 'x' + str(
            self.supported_multipliers_list[0][1])
        mode_strings.append(mode_strings_temp)
        if (write_enable):
            file.write('parameter ' + mode_strings_temp + '\t= ' + str(mode_counter_log) + '\'b00;\n')
        for i in range(0, mode_counter - 1):
            mode_strings_temp = 'mode_sum_' + str(self.supported_multipliers_list[1][i][0]) + 'x' + str(
                self.supported_multipliers_list[1][i][1])
            mode_strings.append(mode_strings_temp)
            if (write_enable):
                file.write('parameter ' + mode_strings_temp + '\t= ' + str(mode_counter_log) + '\'b' + "{0:b}".format(
                i + 1) + ';\n')

        return mode_counter, mode_counter_log, mode_strings


    def Make_unsigned_string(self, sign_flag):
        if sign_flag:
            return ''
        else:
            return 'un'


    def writer_module_top_tb_input_parameters_signals(self, file):

        # write parameters and signals and wires
        # parameters
        self.writer_head_line(file, 'Simulation Hyper parameters')
        file.write('parameter test_max_counter = ' + str(self.test_max_counter) + ';\n')
        file.write('\n')

        mode_counter, mode_counter_log, mode_strings = self.writer_parameter_modes(file, True)
        file.write('reg [' + str(mode_counter_log) + ':0] mode;\n')
        file.write('\n')

        # integers
        file.write('//integers\n')
        file.write('integer counter, Error_counter;\n')
        file.write('\n')

        # inputs & outputs
        self.writer_head_line(file, 'Inputs  & outputs')
        file.write('reg [' + str(self.T_chop_number * self.A_chop_size - 1) + ':0] a;\n')
        file.write('reg [' + str(self.T_chop_number * self.B_chop_size - 1) + ':0] b;\n')
        file.write('\n')
        file.write('reg a_sign;\n')
        file.write('reg b_sign;\n')
        file.write('\n')
        file.write('wire signed [' + str(self.A_width + self.B_width - 1) + ':0] result_0;\n')
        file.write('wire signed [' + str(self.A_width + self.B_width - 1) + ':0] result_1;\n')
        file.write('\n')

        file.write('wire [' + str(
            self.arch_Saving_precision_SE_size * len(self.arch_splitters) - 1) + ':0] result_SIMD_carry;\n')
        file.write('reg [' + str(
            self.arch_Saving_precision_SE_size * len(self.arch_splitters) - 1) + ':0] temp_SIMD_carry;\n')
        file.write('\n')
        file.write('reg signed [' + str(self.A_width + self.B_width - 1) + ':0] result;\n')
        file.write('reg signed [' + str(self.A_width + self.B_width - 1) + ':0] result_ideal;\n')
        file.write('\n')

    def Make_model_files_top_tb(self):
        # This module prepare a test bench for chopped multiplier

        # module and tester name
        module_name = self.module_name_generator('top')
        module_tester_name = module_name + '_tb'

        # open the .v file to write
        file = open(self.output_directory + module_tester_name + '.v', 'w')

        # writing time scale and module name in the file
        self.writer_timescale_and_module_name(file, module_tester_name, 1)
        file.write('\n')

        # writes the parameters, signals and wire of the test bench
        self.writer_module_top_tb_input_parameters_signals(file)

        # writes the clock generator code for test bench
        self.writer_head_line(file, 'Clock generator')
        self.writer_clock_generator(file)
        file.write('\n')

        mode_counter, mode_counter_log, mode_strings = self.writer_parameter_modes(file, False)
        file.write('initial begin\n')
        file.write('\tError_counter = 0;\n')
        file.write('\t@(posedge clk);\n')
        file.write('\t@(posedge clk);\n')
        file.write('\n')

        # Test normal operation
        for a_signed in range(0, 2):  # 0/1 --> unsigned/signed
            for b_signed in range(0, 2):  # 0/1 --> unsigned/signed

                a_unsigned_string = self.Make_unsigned_string(a_signed)
                b_unsigned_string = self.Make_unsigned_string(b_signed)

                file.write(
                    '\t// check ' + a_unsigned_string + 'signed/' + b_unsigned_string + 'signed mult ' + str(
                        self.A_width) + 'x' + str(
                        self.B_width) + '\n')

                file.write('\tfor (counter = 0; counter < test_max_counter; counter = counter + 1) begin \n')
                file.write('\t\t@(posedge clk);\n')
                file.write('\n')

                file.write('\t\ta = $random;\n')
                if (self.T_chop_number * self.A_chop_size - 1 > self.A_width):
                    if(a_signed):
                        file.write('\t\ta[' + str(self.T_chop_number * self.A_chop_size - 1) + ':' + str(
                            self.A_width) + '] = {' + str(
                            self.T_chop_number * self.A_chop_size - self.A_width) + '{a[' + str(
                            self.A_width - 1) + ']}};\n')
                    else:
                        file.write('\t\ta[' + str(self.T_chop_number * self.A_chop_size - 1) + ':' + str(
                            self.A_width) + '] = {' + str(
                            self.T_chop_number * self.A_chop_size - self.A_width) + '{1\'b0}};\n')


                file.write('\t\tb = $random;\n')
                if (self.T_chop_number * self.B_chop_size - 1 > self.B_width):
                    if (b_signed):
                        file.write('\t\tb[' + str(self.T_chop_number * self.A_chop_size - 1) + ':' + str(
                            self.B_width) + '] = {' + str(
                            self.T_chop_number * self.A_chop_size - self.B_width) + '{b[' + str(
                            self.B_width - 1) + ']}};\n')
                    else:
                        file.write('\t\tb[' + str(self.T_chop_number * self.A_chop_size - 1) + ':' + str(
                            self.B_width) + '] = {' + str(
                            self.T_chop_number * self.A_chop_size - self.B_width) + '{1\'b0}};\n')
                file.write('\n')
                file.write('\t\ta_sign = 1\'b' + str(a_signed) + ';\n')
                file.write('\t\tb_sign = 1\'b' + str(b_signed) + ';\n')
                file.write('\n')
                file.write('\t\tmode = ' + mode_strings[0] + ';\n')
                file.write('\n')

                file.write('\t\t#1\n')
                file.write('\n')

                file.write('\t\tresult = result_0 + result_1;\n')

                if (a_signed):
                    a_string = '{{a[' + str(self.A_width-1) + ']},{a}}' #$#  -1
                else:
                    a_string = '{{1\'b0},{a}}'

                if (b_signed):
                    b_string = '{{b[' + str(self.B_width-1) + ']},{b}}' #$#  -1
                else:
                    b_string = '{{1\'b0},{b}}'

                file.write('\t\tresult_ideal = $signed('+a_string+') * $signed('+b_string+');\n')
                file.write('\t\tif (result_ideal != result) begin\n')
                file.write('\t\t\tError_counter = Error_counter + 1;\n')
                file.write('\t\tend\n')

                file.write('\tend\n')
                file.write('\n')

        file.write('\n')

        # Test SIMD operations
        for level in range(0, self.fraction_level + 1):
            for a_signed in range(0, 2):  # 0/1 --> unsigned/signed
                for b_signed in range(0, 2):  # 0/1 --> unsigned/signed

                    a_unsigned_string = self.Make_unsigned_string(a_signed)
                    b_unsigned_string = self.Make_unsigned_string(b_signed)

                    file.write(
                        '\t// check ' + a_unsigned_string + 'signed/' + b_unsigned_string + 'signed/' + ' mult ' + str(
                            self.A_result_mult_size[level]) + 'x' + str(
                            self.B_result_mult_size[level]) + '\n')

                    file.write('\tfor (counter = 0; counter < test_max_counter; counter = counter + 1) begin \n')
                    file.write('\t\t@(posedge clk);\n')
                    file.write('\t\ta = $random;\n')
                    file.write('\t\tb = $random;\n')
                    file.write('\n')
                    file.write('\t\ta_sign = 1\'b' + str(a_signed) + ';\n')
                    file.write('\t\tb_sign = 1\'b' + str(b_signed) + ';\n')
                    file.write('\n')

                    file.write('\t\tmode = ' + mode_strings[level + 1] + ';\n')
                    file.write('\n')

                    file.write('\t\t#1\n')

                    for index in range(pow(2, self.fraction_level - level) - 1, len(self.arch_splitters), pow(2, self.fraction_level - level)):

                        point_start = self.arch_splitters[index]

                        if (index == pow(2, self.fraction_level - level) - 1):
                            point_end = 0
                        else:
                            point_end = self.arch_splitters[index - pow(2, self.fraction_level - level)] + 1

                        points_string = str(point_start) +':'+ str(point_end)

                        file.write('\t\t{{temp_SIMD_carry[' + str((index+1) * self.arch_Saving_precision_SE_size - 1) + ':' + str(
                            index * self.arch_Saving_precision_SE_size) + ']},{result [' + points_string + ']}} = {{result_SIMD_carry[' + str(
                            (index+1) * self.arch_Saving_precision_SE_size - 1) + ':' + str(
                            index * self.arch_Saving_precision_SE_size) + ']},{result_0 [' + points_string + ']}} + {{2\'b00},{result_1 [' + points_string + ']}};\n')

                    file.write('\n')


                    A_strings = []
                    B_strings = []
                    for index_chop in range(0, self.T_chop_number):
                        for index in range(pow(2, level)-1 , -1, -1):

                            if (a_signed):
                                A_string = '$signed({{a[' + str(
                                    index_chop * self.A_chop_size + self.A_result[level][index] - 1) + ']},{a[' + str(
                                    index_chop * self.A_chop_size + self.A_result[level][index] - 1) + ':' + str(
                                    index_chop * self.A_chop_size + self.A_result[level][index] -
                                    self.A_result_mult_size[level]) + ']}})'
                            else:
                                A_string = '$signed({{1\'b0},{a[' + str(
                                    index_chop * self.A_chop_size + self.A_result[level][index] - 1) + ':' + str(
                                    index_chop * self.A_chop_size + self.A_result[level][index] -
                                    self.A_result_mult_size[level]) + ']}})'

                            A_strings.append(A_string)


                            if (b_signed):
                                B_string = '$signed({{b[' + str(
                                    index_chop * self.B_chop_size + self.B_result[level][index] - 1) + ']},{b[' + str(
                                    index_chop * self.B_chop_size + self.B_result[level][index] - 1) + ':' + str(
                                    index_chop * self.B_chop_size + self.B_result[level][index] -
                                    self.B_result_mult_size[
                                        level]) + ']}})'
                            else:
                                B_string = '$signed({{1\'b0},{b[' + str(
                                    index_chop * self.B_chop_size + self.B_result[level][index] - 1) + ':' + str(
                                    index_chop * self.B_chop_size + self.B_result[level][index] -
                                    self.B_result_mult_size[
                                        level]) + ']}})'

                            B_strings.append(B_string)

                    col_main_number = np.int(self.T_chop_number / self.arch_SIMD_hight)
                    col_internal_number = pow(2, level)

                    for col_main in range (0, col_main_number):
                        for col_internal in range(0, col_internal_number):
                            for row in range(0, self.arch_SIMD_hight):
                                index = col_main * self.arch_SIMD_hight * col_internal_number
                                index = index + col_internal + col_internal_number * row

                                if (row == 0):
                                    condition_string = A_strings[index] + '*' + B_strings[index]
                                else:
                                    condition_string = condition_string + ' + ' + A_strings[index] + '*' + B_strings[index]

                            index_result = (col_main * col_internal_number + col_internal) * pow(2, self.fraction_level - level) + pow(2, self.fraction_level - level) - 1

                            point_start = self.arch_splitters[index_result]
                            point_end = self.arch_splitters[index_result] - (
                                        self.A_result_mult_size[level] + self.B_result_mult_size[level]) + 1

                            result_string = '{{temp_SIMD_carry[' + str((index_result+1) * self.arch_Saving_precision_SE_size - 1) + ':' + str(
                            index_result * self.arch_Saving_precision_SE_size) + ']},{result[' + str(point_start) + ':' + str(point_end) + ']}}'

                            condition_string_total = result_string + ' != ' + 'result_ideal[' + str(
                                self.A_result_mult_size[level] + self.B_result_mult_size[level] + self.arch_Saving_precision_SE_size - 1) + ':0]'

                            file.write('\t\tresult_ideal = ' + condition_string + ';\n')
                            file.write('\t\tif  (' + condition_string_total + ') begin\n')
                            file.write('\t\t\tError_counter = Error_counter + 1;\n')
                            file.write('\t\tend\n')
                            file.write('\n')

                    file.write('\tend\n')
                    file.write('\n')

        # reporting the error counter
        file.write('\n')
        file.write('\t$display(" ");\n')
        file.write('\tif (Error_counter != 0)begin\n')
        file.write('\t\t$display("--> Error: there was %d wrong answer", Error_counter);\n')
        file.write('\tend else begin\n')
        file.write('\t\t$display("--> Correct: there was no wrong answer :) ");\n')
        file.write('\tend\n')
        file.write('\t$display(" ");\n')
        file.write('\n')

        # finishing the simulation
        file.write('\n')
        file.write('\t@(posedge clk);\n')
        file.write('\t@(posedge clk);\n')
        file.write('\t$finish();\n')
        file.write('end\n')
        file.write('\n')

        # instantiate the module
        file.write(module_name + '\t' + module_name + '_inst(\n')
        file.write('\t.a(a),\n')
        file.write('\t.b(b),\n')
        file.write('\n')
        file.write('\t.a_sign(a_sign),\n')
        file.write('\t.b_sign(b_sign),\n')
        file.write('\n')
        file.write('\t.mode(mode),\n')
        file.write('\n')
        file.write('\t.result_0(result_0),\n')
        file.write('\t.result_1(result_1),\n')
        file.write('\t.result_SIMD_carry(result_SIMD_carry)\n')
        file.write(');\n')

        # writing the end of Verilog file (endmodule)
        self.writer_end_module(file)

        # closing the file
        file.close()

    def Make_ALU_files_SIMD(self):
        # This module prepare a SIMD parameterized ALU module

        # module and tester name
        module_name = self.module_name_generator('alu_s')
        #module_tester_name = module_name + '_tb'

        # open the .v file to write
        file = open(self.output_directory + module_name + '.v', 'w')

        # writing time scale and module name in the file
        self.writer_timescale_and_module_name(file, module_name, 0)
        file.write('\n')

        parameter_s = 'Width'
        parameter_s_1 = parameter_s + '-1'
        file.write('\t\tinput [' + parameter_s_1 + ':0] W,\n')
        file.write('\t\tinput [' + parameter_s_1 + ':0] Z,\n')
        file.write('\t\tinput [' + parameter_s_1 + ':0] Y,\n')
        file.write('\t\tinput [' + parameter_s_1 + ':0] X,\n')
        file.write('\n')

        file.write('\t\tinput [1:0] op,\n')
        file.write('\t\tinput Z_controller,\n')
        file.write('\t\tinput S_controller,\n')
        file.write('\t\tinput W_X_Y_controller,\n')
        file.write('\t\tinput [1:0] CIN_W_X_Y_CIN,\n')
        file.write('\t\tinput CIN_Z_W_X_Y_CIN,\n')

        file.write('\n')
        file.write('\t\toutput [' + parameter_s_1 + ':0] S,\n')
        file.write('\n')
        file.write('\t\toutput [1:0] COUT_W_X_Y_CIN,\n')

        if (self.parameter_optimization_ALU_CarryLookAHead == 0):
            file.write('\t\toutput COUT_Z_W_X_Y_CIN,\n')
        else:
            file.write('\t\toutput reg COUT_Z_W_X_Y_CIN,\n')

        file.write('\n')
        file.write('\t\tinput [' + str(self.arch_Saving_precision_SE_size-1) + ':0] result_SIMD_carry_in,\n')
        file.write('\t\toutput [' + str(self.arch_Saving_precision_SE_size-1) + ':0] result_SIMD_carry_out\n')


        file.write('\t);\n')
        file.write('\n')
        file.write('//parameters\n')
        file.write('parameter ' + parameter_s + ' = 8;\n')
        file.write('\n')
        file.write('// controllable not\n')
        file.write('wire [' + parameter_s_1 + ':0] Z_Z_bar;\n')
        file.write('assign Z_Z_bar 	= Z ^ {' + parameter_s + '{Z_controller}};\n')
        file.write('\n')
        file.write('// logical part\n')
        file.write('wire [' + parameter_s_1 + ':0] out_and;\n')
        file.write('wire [' + parameter_s_1 + ':0] out_or;\n')
        file.write('wire [' + parameter_s_1 + ':0] out_xor;\n')
        file.write('assign out_and 	= X & Z_Z_bar;\n')
        file.write('assign out_or   = X | Z_Z_bar;\n')
        file.write('assign out_xor 	= X ^ Z_Z_bar ^ Y;\n')
        file.write('\n')
        file.write('//computations\n')
        file.write('wire [' + parameter_s_1 + ':0] temp_W_X_Y;\n')
        file.write('assign {{COUT_W_X_Y_CIN}, {temp_W_X_Y}} = W + X + Y + CIN_W_X_Y_CIN;\n')
        file.write('\n')


        file.write('wire [' + parameter_s_1 + ':0] temp_W_X_Y_xored;\n')
        #file.write('assign temp_W_X_Y_xored = {' + str(12) + '{W_X_Y_controller}} ^  temp_W_X_Y;\n')

        file.write('wire [' + parameter_s_1 + ':0] W_X_Y_controller_wide;\n')
        file.write('generate\n')
        file.write('\tassign W_X_Y_controller_wide = {' + parameter_s + '{W_X_Y_controller}};\n')
        file.write('endgenerate\n')
        file.write('assign temp_W_X_Y_xored = W_X_Y_controller_wide ^  temp_W_X_Y;\n')
        file.write('\n')


        file.write('wire [' + parameter_s + ':0] S_temp_sum;\n')


        if(self.parameter_optimization_ALU_CarryLookAHead == 0):

            file.write('assign {{COUT_Z_W_X_Y_CIN},{S_temp_sum}} = temp_W_X_Y_xored + Z_Z_bar + CIN_Z_W_X_Y_CIN;\n')
        else:

            file.write('assign S_temp_sum = temp_W_X_Y_xored + Z_Z_bar + CIN_Z_W_X_Y_CIN;\n')
            ##
            file.write('\n')
            file.write('\n')
            file.write('reg [' + parameter_s_1 + ':0] CLA_temp_AND [' + parameter_s + ':0];\n')
            file.write('reg [' + parameter_s + ':0] CLA_temp_AND_r ;\n')
            file.write('reg [' + parameter_s + ':0] CLA_temp_OR ;\n')
            file.write('integer CLA_iter_1;\n')
            file.write('integer CLA_iter_2;\n')
            file.write('always@(*)begin\n')
            file.write('\tfor(CLA_iter_1 = Width; CLA_iter_1 > -1; CLA_iter_1 = CLA_iter_1 - 1)begin\n')
            file.write('\t\tfor(CLA_iter_2 = Width - 1; CLA_iter_2 > -1; CLA_iter_2 = CLA_iter_2 - 1)begin\n')
            file.write('\t\t\tCLA_temp_AND[CLA_iter_1][CLA_iter_2] = 1\'b1;\n')
            file.write('\t\tend\n')
            file.write('\tend\n')
            file.write('\tfor(CLA_iter_1 = Width; CLA_iter_1 > -1; CLA_iter_1 = CLA_iter_1 - 1)begin\n')
            file.write('\t\tfor(CLA_iter_2 = Width - 1; CLA_iter_2 > CLA_iter_1 - 1; CLA_iter_2 = CLA_iter_2 - 1)begin\n')
            file.write('\t\t\tCLA_temp_AND[CLA_iter_1][CLA_iter_2] = Z_Z_bar[CLA_iter_2] ^ temp_W_X_Y_xored[CLA_iter_2];\n')
            file.write('\t\tend\n')
            file.write('\t\tif (CLA_iter_1 == 0) begin\n')
            file.write('\t\t\tCLA_temp_AND_r[CLA_iter_1] = CIN_Z_W_X_Y_CIN;\n')
            file.write('\t\tend else begin\n')
            file.write('\t\t\tCLA_temp_AND_r[CLA_iter_1] = Z_Z_bar[CLA_iter_1 - 1] & temp_W_X_Y_xored[CLA_iter_1 - 1];\n')
            file.write('\t\tend\n')
            file.write('\tend\n')
            file.write('\tfor(CLA_iter_1 = Width; CLA_iter_1 > -1; CLA_iter_1 = CLA_iter_1 - 1)begin\n')
            file.write('\t\tCLA_temp_OR[CLA_iter_1] = (&CLA_temp_AND[CLA_iter_1]) & (CLA_temp_AND_r[CLA_iter_1]);\n')
            file.write('\tend\n')
            file.write('\tCOUT_Z_W_X_Y_CIN = (|CLA_temp_OR);\n')
            file.write('end\n')
            file.write('\n')
            file.write('\n')

        file.write('\n')
        file.write('assign result_SIMD_carry_out = result_SIMD_carry_in + COUT_W_X_Y_CIN + COUT_Z_W_X_Y_CIN;\n')
        file.write('\n')
        file.write('reg [' + parameter_s_1 + ':0] S_temp_selected;\n')
        file.write('\n')
        file.write('always@(*)begin\n')
        file.write('\tcase (op)\n')
        file.write('\t\t2\'b00: S_temp_selected = S_temp_sum;\n')
        file.write('\t\t2\'b01: S_temp_selected = out_xor;\n')
        file.write('\t\t2\'b10: S_temp_selected = out_and;\n')
        file.write('\t\t2\'b11: S_temp_selected = out_or;\n')
        file.write('\tendcase\n')
        file.write('end\n')
        file.write('\n')

        file.write('generate\n')
        file.write('\tassign S = S_temp_selected ^ {' + parameter_s + '{S_controller}};\n')
        file.write('endgenerate\n')

        # writing the end of Verilog file (endmodule)
        self.writer_end_module(file)

        # closing the file
        file.close()

    def Make_ALU_files_SIMD_tb(self):
        # This module prepare a tester for SIMD parameterized ALU module

        # module and tester name
        module_name = self.module_name_generator('alu_s')
        module_tester_name = module_name + '_tb'

        # open the .v file to write
        file = open(self.output_directory + module_tester_name + '.v', 'w')

        # writing time scale and module name in the file
        self.writer_timescale_and_module_name(file, module_tester_name, 1)
        file.write('\n')

        # writes the clock generator code for test bench
        self.writer_head_line(file, 'Clock generator')
        self.writer_clock_generator(file)
        file.write('\n')

        # write parameters and signals and wires
        # parameters
        self.writer_head_line(file, 'Simulation Hyper parameters')
        file.write('parameter test_max_counter = ' + str(self.test_max_counter) + ';\n')
        file.write('parameter Width = 8;\n')
        file.write('\n')

        # integers
        file.write('//integers\n')
        file.write('integer counter, Error_counter;\n')
        file.write('\n')

        # inputs & outputs
        self.writer_head_line(file, 'Inputs  & outputs')
        file.write('reg [Width-1:0] W;\n')
        file.write('reg [Width-1:0] Z;\n')
        file.write('reg [Width-1:0] Y;\n')
        file.write('reg [Width-1:0] X;\n')
        file.write('\n')
        file.write('reg [1:0] op;\n')
        file.write('reg Z_controller;\n')
        file.write('reg S_controller;\n')
        file.write('reg W_X_Y_controller;\n')
        file.write('reg [1:0] CIN_W_X_Y_CIN;\n')
        file.write('reg CIN_Z_W_X_Y_CIN;\n')
        file.write('\n')
        file.write('wire [Width-1:0] S;\n')
        file.write('\n')
        file.write('wire [1:0] COUT_W_X_Y_CIN;\n')
        file.write('wire COUT_Z_W_X_Y_CIN;\n')
        file.write('\n')
        file.write('reg [1:0] result_SIMD_carry_in;\n')
        file.write('wire [1:0] result_SIMD_carry_out;\n')
        file.write('\n')
        file.write('reg [Width+1:0] S_temp;\n')
        file.write('reg [1:0] carry_temp;\n')

        file.write('initial begin\n')
        file.write('\tError_counter = 0;\n')
        file.write('\top = 2\'b0;\n')
        file.write('\tZ_controller = 0;\n')
        file.write('\tS_controller = 0;\n')
        file.write('\tW_X_Y_controller = 0;\n')
        file.write('\tCIN_W_X_Y_CIN = 2\'b0;\n')
        file.write('\tCIN_Z_W_X_Y_CIN = 0;\n')
        file.write('\tresult_SIMD_carry_in = 0;\n')
        file.write('\n')
        file.write('\t@(posedge clk);\n')
        file.write('\t@(posedge clk);\n')
        file.write('\tfor (counter = 0; counter < test_max_counter; counter = counter + 1) begin \n')
        file.write('\t\t@(posedge clk);\n')
        file.write('\n')
        file.write('\t\tW = $random;\n')
        file.write('\t\tZ = $random;\n')
        file.write('\t\tY = $random;\n')
        file.write('\t\tX = $random;\n')
        file.write('\n')
        file.write('\t\t#1\n')
        file.write('\t\tS_temp = W + Z + X + Y;\n')
        file.write('\t\tif  (S_temp[Width-1:0] != S ) begin\n')
        file.write('\t\t\tError_counter = Error_counter + 1;\n')
        file.write('\t\tend\n')
        file.write('\n')
        file.write('\t\tcarry_temp = COUT_W_X_Y_CIN + COUT_Z_W_X_Y_CIN;\n')
        file.write('\t\tif  (S_temp[Width+1:Width] != carry_temp ) begin\n')
        file.write('\t\t\tError_counter = Error_counter + 1;\n')
        file.write('\t\tend\n')
        file.write('\n')

        file.write('\tend\n')
        file.write('end\n')

        file.write('ALU_SIMD_Width_parameterized_HighLevelDescribed_auto ALU_SIMD_Width_parameterized_HighLevelDescribed_auto_inst(\n')
        file.write('\t.W(W),\n')
        file.write('\t.Z(Z),\n')
        file.write('\t.Y(Y),\n')
        file.write('\t.X(X),\n')
        file.write('\n')
        file.write('\t.op(op),\n')
        file.write('\t.Z_controller(Z_controller),\n')
        file.write('\t.S_controller(S_controller),\n')
        file.write('\t.W_X_Y_controller(W_X_Y_controller),\n')
        file.write('\t.CIN_W_X_Y_CIN(CIN_W_X_Y_CIN),\n')
        file.write('\t.CIN_Z_W_X_Y_CIN(CIN_Z_W_X_Y_CIN),\n')
        file.write('\t\n')
        file.write('\t.S(S),\n')
        file.write('\t\n')
        file.write('\t.COUT_W_X_Y_CIN(COUT_W_X_Y_CIN),\n')
        file.write('\t.COUT_Z_W_X_Y_CIN(COUT_Z_W_X_Y_CIN),\n')
        file.write('\t\n')
        file.write('\t.result_SIMD_carry_in(result_SIMD_carry_in),\n')
        file.write('\t.result_SIMD_carry_out(result_SIMD_carry_out)\n')
        file.write(');\n')
        file.write('\n')





        # writing the end of Verilog file (endmodule)
        self.writer_end_module(file)

        # closing the file
        file.close()

    def Make_ALU_files_top(self):
        # This module prepare the ALU module

        # module and tester name
        module_name = self.module_name_generator('alu_t')

        # open the .v file to write
        file = open(self.output_directory + module_name + '.v', 'w')

        file.write('/*****************************************************************\n')
        file.write('*	Configuration bits order : Nothing\n')
        file.write('*****************************************************************/\n')
        # writing time scale and module name in the file
        self.writer_timescale_and_module_name(file, module_name, 0)

        mode_counter, mode_counter_log, mode_strings = self.writer_parameter_modes(file, False)

        file.write('\t\tinput [3:0] ALUMODE,\n')
        file.write('\t\tinput [8:0] OPMODE,\n')
        file.write('\n')
        file.write('\t\tinput [' + str(mode_counter_log - 1) + ':0] USE_SIMD,\n')
        file.write('\t\t\n')
        file.write('\t\tinput [' + str(self.arch_splitters[-1]) + ':0] W,\n')
        file.write('\t\tinput [' + str(self.arch_splitters[-1]) + ':0] Z,\n')
        file.write('\t\tinput [' + str(self.arch_splitters[-1]) + ':0] Y,\n')
        file.write('\t\tinput [' + str(self.arch_splitters[-1]) + ':0] X,\n')
        file.write('\n')
        file.write('\t\tinput CIN,\n')
        file.write('\t\t\n')
        file.write('\t\toutput [' + str(self.arch_splitters[-1]) + ':0] S,\n')
        file.write('\t\t\n')
        file.write('\t\tinput [' + str(
            self.arch_Saving_precision_SE_size * len(self.arch_splitters) - 1) + ':0] result_SIMD_carry_in,\n')
        file.write('\t\toutput [' + str(
            self.arch_Saving_precision_SE_size * len(self.arch_splitters)-1) + ':0] result_SIMD_carry_out\n')
        file.write(');\n')

        file.write('//Mode parameters\n')
        self.writer_parameter_modes(file, True);

        file.write('// ALU\n')
        file.write('parameter op_sum 	= 2\'b00;\n')
        file.write('parameter op_xor 	= 2\'b01;\n')
        file.write('parameter op_and 	= 2\'b10;\n')
        file.write('parameter op_or 	= 2\'b11;\n')
        file.write('\n')
        file.write('reg Z_controller;\n')
        file.write('always@(*)begin\n')
        file.write('\tcase (ALUMODE)\n')
        file.write('\t\t4\'b0011: Z_controller = 0;\n')
        file.write('\t\tdefault: Z_controller = ALUMODE[0];\n')
        file.write('\tendcase\n')
        file.write('end\n')
        file.write('\n')
        file.write('reg S_controller;\n')
        file.write('always@(*)begin\n')
        file.write('\tcase (ALUMODE)\n')
        file.write('\t\t4\'b0011: S_controller = 0;\n')
        file.write('\t\tdefault: S_controller = ALUMODE[1];\n')
        file.write('\tendcase\n')
        file.write('end\n')
        file.write('\n')
        file.write('wire W_X_Y_controller;\n')
        file.write('assign W_X_Y_controller = ALUMODE[1] && ALUMODE[0];\n')
        file.write('\n')
        file.write('reg [1:0] op;\n')
        file.write('\n')
        file.write('always@(*)begin\n')
        file.write('\tcase (ALUMODE[3:2])\n')
        file.write('\t\t2\'b00: op = op_sum;\n')
        file.write('\t\t2\'b01: op = op_xor;\n')
        file.write('\t\t2\'b11: begin \n')
        file.write('\t\t\tif (OPMODE[3])\n')
        file.write('\t\t\t\top = op_or;\n')
        file.write('\t\t\telse \n')
        file.write('\t\t\t\top = op_and;\n')
        file.write('\t\tend\n')
        file.write('\t\tdefault: op = 2\'bxx;\n')
        file.write('\tendcase\n')
        file.write('end\n')
        file.write('\n')
        file.write('reg [1:0] CIN_W_X_Y_CIN [' + str(len(self.arch_splitters) - 1) + ':0];\n')
        file.write('reg [' + str(len(self.arch_splitters) - 1) + ':0] CIN_Z_W_X_Y_CIN;\n')
        file.write('\n')
        file.write('wire [1:0] COUT_W_X_Y_CIN [' + str(len(self.arch_splitters) - 1) + ':0];\n')
        file.write('wire [' + str(len(self.arch_splitters) - 1) + ':0] COUT_Z_W_X_Y_CIN;\n')
        file.write('\n')
        file.write('always@(*)begin\n')
        file.write('\tcase (USE_SIMD)\n')

        for mode in range(0, mode_counter+1):
            if (mode == mode_counter):
                mode_s = 'default'
            else:
                mode_s = mode_strings[mode]

            file.write('\t\t' + mode_s + ': begin\n')


            for index in range(0, len(self.arch_splitters)):
                if (mode == 0):
                    if (index == 0):
                        file.write('\t\t\tCIN_W_X_Y_CIN[' + str(index) + '] = {{1\'b0}, {CIN}};\n')
                    else:
                        file.write('\t\t\tCIN_W_X_Y_CIN[' + str(index) + '] = COUT_W_X_Y_CIN[' + str(index-1) + '];\n')

                elif (mode == mode_counter):
                    file.write('\t\t\tCIN_W_X_Y_CIN[' + str(index) + '] = 2\'bx;\n')
                else:

                    if (index % int(pow(2, mode_counter - 1 - mode)) == 0):
                        file.write('\t\t\tCIN_W_X_Y_CIN[' + str(index) + '] = {2\'b0};\n')
                    else:
                        file.write(
                            '\t\t\tCIN_W_X_Y_CIN[' + str(index) + '] = COUT_W_X_Y_CIN[' + str(index - 1) + '];\n')

            file.write('\n')

            for index in range(0, len(self.arch_splitters)):
                if (mode == 0):
                    if (index == 0):
                        file.write('\t\t\tCIN_Z_W_X_Y_CIN[' + str(index) + '] = Z_controller;\n')
                    else:
                        file.write('\t\t\tCIN_Z_W_X_Y_CIN[' + str(index) + '] = COUT_Z_W_X_Y_CIN[' + str(index-1) + '];\n')
                elif (mode == mode_counter):
                    file.write('\t\t\tCIN_Z_W_X_Y_CIN[' + str(index) + '] = 1\'bx;\n')
                else:
                    if (index % int(pow(2, mode_counter - 1 - mode)) == 0):
                        file.write('\t\t\tCIN_Z_W_X_Y_CIN[' + str(index) + '] = Z_controller;\n')
                    else:
                        file.write(
                            '\t\t\tCIN_Z_W_X_Y_CIN[' + str(index) + '] = COUT_Z_W_X_Y_CIN[' + str(index - 1) + '];\n')

            file.write('\t\tend\n')

        file.write('\tendcase\n')
        file.write('end\n')

        module_name_sub = self.module_name_generator('alu_s')
        for index in range(0, len(self.arch_splitters)):

            if (index == 0):
                index_s = 0
                index_e = self.arch_splitters[index]
                delta = self.arch_splitters[index]+1
            else:
                index_s = self.arch_splitters[index - 1] + 1
                index_e = self.arch_splitters[index]
                delta = index_e - index_s + 1

            file.write('defparam '+ module_name_sub +'_inst' + str(index) + '.Width = ' + str(delta) + ';\n')
            file.write(module_name_sub + '\t' + module_name_sub + '_inst' + str(index) + '(\n')

            file.write('\t.W(W[' + str(index_e) + ':' + str(index_s) + ']),\n')
            file.write('\t.Z(Z[' + str(index_e) + ':' + str(index_s) + ']),\n')
            file.write('\t.Y(Y[' + str(index_e) + ':' + str(index_s) + ']),\n')
            file.write('\t.X(X[' + str(index_e) + ':' + str(index_s) + ']),\n')
            file.write('\t\n')
            file.write('\t.op(op),\n')
            file.write('\t.Z_controller(Z_controller),\n')
            file.write('\t.S_controller(S_controller),\n')
            file.write('\t.W_X_Y_controller(W_X_Y_controller),\n')
            file.write('\t.CIN_W_X_Y_CIN(CIN_W_X_Y_CIN[' + str(index) + ']),\n')
            file.write('\t.CIN_Z_W_X_Y_CIN(CIN_Z_W_X_Y_CIN[' + str(index) + ']),\n')
            file.write('\t\n')
            file.write('\t.S(S[' + str(index_e) + ':' + str(index_s) + ']),\n')
            file.write('\t\n')
            file.write('\t.COUT_W_X_Y_CIN(COUT_W_X_Y_CIN[' + str(index) + ']),\n')
            file.write('\t.COUT_Z_W_X_Y_CIN(COUT_Z_W_X_Y_CIN[' + str(index) + ']),\n')
            file.write('\t\n')
            file.write('\t.result_SIMD_carry_in(result_SIMD_carry_in[' + str(
                (index+1) * self.arch_Saving_precision_SE_size-1) + ':' + str(
                index * self.arch_Saving_precision_SE_size) + ']),\n')
            file.write('\t.result_SIMD_carry_out(result_SIMD_carry_out[' + str(
                (index+1) * self.arch_Saving_precision_SE_size-1) + ':' + str(
                index * self.arch_Saving_precision_SE_size) + '])\n')
            file.write(');\n')
            file.write('\n')


        # writing the end of Verilog file (endmodule)
        self.writer_end_module(file)

        # closing the file
        file.close()


    def Make_model_files(self):
        # calling the methods which are responsible for making Verilog files
        print('Writing the model files is started')
        self.Make_model_files_chopped()
        self.Make_model_files_chopped_tb()
        self.Make_model_files_top()
        self.Make_model_files_top_tb()
        self.Make_ALU_files_SIMD()
        self.Make_ALU_files_SIMD_tb()
        self.Make_ALU_files_top()
        print('Writing the model files is finished')
