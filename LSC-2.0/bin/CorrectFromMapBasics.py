import sys, re
from math import log

# Probability of correctness
fq_prob_list = [0.725,
                0.9134,
                0.936204542,
                0.949544344,
                0.959009084,
                0.966350507,
                0.972348887,
                0.977420444,
                0.981813627,
                0.985688689,
                0.98915505,
                0.992290754,
                0.995153429,
                0.997786834,
                0.999999999]
fq_char_list = [str(unichr(min(int(33 - 10 * log(1 -p,10)), 73))) for p in fq_prob_list]
NUM_FQ_CHAR = len(fq_char_list) - 1


################################################################################
# Separate the path to a file from the filename (filepath -> path,filename)
def GetPathAndName(pathfilename):
    ls=pathfilename.split('/')
    filename=ls[-1]
    if len(ls)==1:
        return '',filename
    path='/'.join(ls[0:-1])+'/'
    return path, filename

# Compute the complementary sequence from a base sequence
def compleseq(seq):
    newseq=""
    for base in seq:
        if base=="A":
            base="T"
        elif base=="C":
            base="G"
        elif base=="G":
            base="C"
        elif base=="T":
            base="A"
        elif base=="-":
            base="-"
        elif base=="a":
            base="t"
        elif base=="c":
            base="g"
        elif base=="g":
            base="c"
        elif base=="t":
            base="a"

        newseq=base+newseq
    return newseq

def lower_mismatch_bowtie(SR_seq,mismatch):
    if mismatch == ['']:
        return SR_seq
    SR_seq_list = list(SR_seq)
    for c in mismatch:
        pos = int(c.split(':')[0])
        SR_seq_list[pos] = SR_seq_list[pos].lower()
    return ''.join(SR_seq_list)

# Turn a cps repetition count list into a complete list (insert 1 for things which aren't repeated)
def expandidx_list(line,onestr):
    L_p_seq_ls = []
    ls = line.strip().split('\t')

    if (len(ls)<2): 
        L_ls=[]
        p_ls=[]
    else:
        p_ls = ls[0].split(',')
        L_ls = ls[1].split(',')

    temp_p=-1
    i=0
    for p in p_ls:
        L_p_seq_ls.extend( [onestr]*(int(p)-temp_p-1))
        L_p_seq_ls.append(L_ls[i])
        temp_p=int(p)
        i+=1
    return L_p_seq_ls

################################################################################
# Compute majority sequence from the candidates
def optimize_seq(temp_candidate_ls):
    result = ""
    max_n = 0
    temp_candidate_set = set(temp_candidate_ls)
    for temp_candidate in temp_candidate_set:
        if temp_candidate!='' :
            n = temp_candidate_ls.count(temp_candidate)
            if n > max_n:
                result = temp_candidate
                max_n =n
    return[ result, max_n ]
################################################################################
# Uncompress a cps back to the original sequence
def uncompress_seq(temp_SR_idx_seq_list,seq):
    result = ""

    i=0
    for s in seq:
        result=result+s*int(temp_SR_idx_seq_list[i])
        i+=1
    return result

def Convertord(SR_idx_seq_list):
    result = ''
    for s in SR_idx_seq_list:
        result = result + chr(int(s)+48)
    return result

class CorrectFromMapFactory:
  def __init__(self,LR_readname_filename):
    self.LR_read_name_list = [""]
    readname_file = open(LR_readname_filename,'r')
    i = 0
    # Load all the long read names
    for line in readname_file:
      i = i + 1
      fields = line.strip().split()
      read_int = int(fields[0])
    
      for j in range(i - read_int):
        # Fill in missing readname entries
        self.LR_read_name_list.append("")
      self.LR_read_name_list.append(fields[1])
    

    #path,filename = GetPathAndName(LR_SR_mapping_filename)

    #self.inf = open(LR_SR_mapping_filename,'r')
    #full_read_file=open(output_prefix+'_full','w')
    #corrected_read_file=open(output_prefix+ '_corrected','w')
    #corrected_read_fq_file=open(output_prefix+'_corrected_fq','w')
    #uncorrected_read_file = open(output_prefix+'_uncorrected','w')

    self.zerostr="0"
    self.onestr="1"

  # For each long read, perform correction
  def correct_map_line(self,map_line):
    # Separate the map line into it's components
    tmp_ls = map_line.rstrip().split('yue')
    LR_seq = tmp_ls[0]
    LR_idx_seq = tmp_ls[1]
    SR_ls_ls = tmp_ls[2].split(';')
    read_name = tmp_ls[3]
    read_int = int(read_name[0:])
    
    if tmp_ls[2] == '':
        sys.stderr.write(read_name + "\tno alignment\n")
        return None

    ls_SR_seq = tmp_ls[4].split('kinfai')
    ls_SR_idx_seq = tmp_ls[5].split('kinfai')
    
    start_pt_ls = []
    NSR_ls = []
    mismatch_ls = []
    indel_pt_set_ls = []
    insert_pt_ls_ls = []
    del_pt_list = []
    del_pt_set=set()
    crt_pt_ls = set()
    crt_pt_dict={}
    all_seq_idx_list=[]
    all_del_seq_list=[]
    temp_all_seq_idx=[]

    LR_seq = LR_seq.strip()+'ZX'*25 # extend the long read with ZX in order to handle short reads which go past the end of the long read
    L_LR_seq = len(LR_seq)
    a=L_LR_seq-1
    LR_idx_seq_ls = LR_idx_seq.strip().split('\t')

    if len(LR_idx_seq_ls) > 1:
        p_ls = LR_idx_seq_ls[0].strip().split(',')
    else:
        p_ls=[]

    crt_pt_ls.update(set([int(x) for x in p_ls]))
    crt_pt_ls.update(set(range(a-50,a) ))
#########################################################################################################
    end_pt_ls = []
    i=0 

    # For each short read mapped to this long read
    coverage_list = [0] * L_LR_seq
    for SR in SR_ls_ls:
        SR_ls = SR.split(',')

        pos = int(SR_ls[1])
        pos -=1
        if pos<0:
            i+=1
            continue
        start_pt_ls.append(pos)
        SR_seq = ls_SR_seq[i]
        L =len(SR_seq.strip())
        NSR_ls.append(SR_ls[0])

        mismatch= SR_ls[2]
        insert_pt_set= set()
        temp_del_dt= {}
        indel_pt_set =set()

        # If there's a mismatch (of any kind) between the SR and LR
        if not mismatch == '':
            mismatch_pos_ls = map(int, re.findall(r'\d+',mismatch))
            mismatch_type_ls = re.findall('>|\+|-', mismatch)
            mismatch_seq_ls = re.findall('\w+', mismatch)
            j=0
            
            # For all of the mismatches
            for mismatch_type in mismatch_type_ls:
                # Convert the CIGAR information into an internal representation by position
                if mismatch_type == '+':
                    del_pt = mismatch_pos_ls[j] + pos
                    del_pt_set.add(del_pt)

                    temp_del_dt[mismatch_pos_ls[j]] = mismatch_seq_ls[2*j+1]
                    indel_pt_set.add(mismatch_pos_ls[j])
                    L -= len(mismatch_seq_ls[2*j+1])
                elif mismatch_type == '-':
                    L_insert = len(mismatch_seq_ls[2*j+1])
                    L += L_insert
                    if L_insert>1:
                        sys.stderr.write("warning inert >2 bp\n")

                    insert_pt_set.add(mismatch_pos_ls[j])
                    indel_pt_set.add(mismatch_pos_ls[j])

                else:
                    p_ls.append(mismatch_pos_ls[j])
                j+=1

        # Compute coverage information (percentage of LR covered by SR)
        end_pt_ls.append(pos + L - 1)
        n_rep = int(SR_ls[0].split('_')[1])
        coverage_list[pos : (pos + L)] = [(coverage_list[k] + n_rep) for k in range(pos, pos + L)]
        
        insert_pt_ls_ls.append(insert_pt_set)
        del_pt_list.append(temp_del_dt)
        indel_pt_set_ls.append(indel_pt_set)
        i+=1

    start_pt =min(start_pt_ls)

########################################################################################################
    if start_pt_ls == []:
        sys.stderr.write(read_name+"\n")
        sys.stderr.write("no alignments, empty\n")

        return None

#########################################################################################################
    # Clip the 3 and 5 prime ends of the long read, which are uncovered by short reads
    temp_LR_idx_seq_list = expandidx_list(LR_idx_seq,self.onestr)
    temp_LR_idx_seq_list.extend( [self.onestr]*( len(LR_seq) - len(temp_LR_idx_seq_list)) ) # handle the ZX stuff

    #max_start_pt100 = 100 + max(start_pt_ls)
    end_pt = max(end_pt_ls)+1

    five_end_seq = uncompress_seq(temp_LR_idx_seq_list[0:(start_pt+1)], LR_seq[0:(start_pt+1)])    # Note: the end and start pos of SRs are not used for correction
    three_end_seq=""
    if ((end_pt-1) < (len(LR_seq)-50)):
        three_end_seq = uncompress_seq(temp_LR_idx_seq_list[(end_pt-1):(len(LR_seq)-50)], LR_seq[(end_pt-1):(len(LR_seq)-50)])


    temp_LR_seq = LR_seq[start_pt:end_pt].strip()
    coverage_list = [ fq_char_list[min( coverage_list[i], NUM_FQ_CHAR)] for i in range(start_pt, end_pt)]
    L_temp_LR_seq = len(temp_LR_seq)

    temp_LR_idx_seq_list = temp_LR_idx_seq_list[start_pt:end_pt]
    temp_LR_idx_seq_list.extend( [self.onestr]*( L_temp_LR_seq - len(temp_LR_idx_seq_list)) )

    output = {}
    output['name'] = self.LR_read_name_list[read_int]
    output['uncorrected_fasta']  = '>' + self.LR_read_name_list[read_int] +"\n"
    # Note: the end and start pos of SRs are not used for correction
    L_temp_LR_idx_seq_list = len(temp_LR_idx_seq_list)
    output['uncorrected_fasta'] += uncompress_seq(temp_LR_idx_seq_list[1:(L_temp_LR_idx_seq_list-1)], temp_LR_seq[1:(L_temp_LR_idx_seq_list-1)]).replace('X','').replace('Z','') +"\n"

#########################################################################################################
    i=0
    # Iterate over the short reads, make the short read as long as the long read (TODO: HOLY SCHAMOLY!)
    for NSR in NSR_ls:
        insert_pt_set = insert_pt_ls_ls[i]
        temp_del_dt = del_pt_list[i]
        indel_pt_set = indel_pt_set_ls[i]
        len_space = start_pt_ls[i]

        SR_seq = ls_SR_seq[i]
        SR_idx_seq = ls_SR_idx_seq[i]

        i+=1

        n_rep = int(NSR.split('_')[1])

        ls = SR_idx_seq.strip().split('\t')
        if len(ls)==0:
            p_ls=[]
        else:
            p_ls = ls[0].split(',')

        SR_idx_seq_list = expandidx_list(SR_idx_seq,self.onestr)
        SR_idx_seq_list.extend([self.onestr]*(len(SR_seq)-len(SR_idx_seq_list)))

        if NSR[0]=='-':
            SR_seq = compleseq(SR_seq)
            SR_idx_seq_list = SR_idx_seq_list[::-1]

        SR_seq_list=list(SR_seq)
        SR_idx_seq_list[0]=self.zerostr
        SR_idx_seq_list[-1]= self.zerostr
        SR_del_seq_list = ['=']*len(SR_seq_list) # Equals sign is used to indicate a deletion

        deleted_idx_list=[]
        indel_pt_ls = list(indel_pt_set)
        indel_pt_ls.sort()
         
        # Go over all the indel points for this short read and rewrite them to use the long read position
        for pt in indel_pt_ls:
            if pt in insert_pt_set:
                SR_seq_list.insert(pt-1,'-')
                SR_idx_seq_list.insert(pt-1,self.onestr)    
                SR_del_seq_list.insert(pt-1,'=')    

            if temp_del_dt.has_key(pt):
                L=len(temp_del_dt[pt])
                pt-=1
                del SR_seq_list[pt:pt+L]
                del SR_del_seq_list[pt:pt+L]    
                SR_del_seq_list[pt-1] = uncompress_seq(SR_idx_seq_list[pt:pt+L], temp_del_dt[pt+1])
                del SR_idx_seq_list[pt:pt+L]
        SR_del_seq = ''.join(SR_del_seq_list)
###############
        I_ls = [x+len_space for x in range(len(SR_idx_seq_list)) if int(SR_idx_seq_list[x]) > 1]
        crt_pt_ls.update(set(I_ls))
#############DISPLAY#######################################
        # Add everything we can learn from this SR into the master correction list
        crt_pt_ls.update( set([int(x)+len_space-1 for x in insert_pt_set]))
        SR_idx_seq  = Convertord(SR_idx_seq_list)
        SR_seq = ''.join(SR_seq_list)

############FILL UP LEFT SIDE############################
        temp_SR_seq = self.zerostr*(len_space-start_pt) + SR_seq
        temp_SR_idx_seq = self.zerostr*(len_space-start_pt) + SR_idx_seq
        temp_SR_del_seq = self.zerostr*(len_space-start_pt) + SR_del_seq

        temp = SR_seq_list[:]
        SR_seq_list = [self.zerostr]*(len_space-start_pt)
        SR_seq_list.extend(temp)

        temp = SR_idx_seq_list[:]
        SR_idx_seq_list =[self.zerostr]*(len_space-start_pt)
        SR_idx_seq_list.extend(temp)

        temp = SR_del_seq_list[:]
        SR_del_seq_list =[self.zerostr]*(len_space-start_pt)
        SR_del_seq_list.extend(temp)

############FILL UP RIGHT SIDE############################

        temp_SR_seq = temp_SR_seq + self.zerostr*(L_temp_LR_seq - len(temp_SR_seq))
        temp_SR_idx_seq = temp_SR_idx_seq + self.zerostr*(L_temp_LR_seq - len(temp_SR_idx_seq))
        temp_SR_del_seq = temp_SR_del_seq + self.zerostr*(L_temp_LR_seq - len(temp_SR_del_seq))

        SR_seq_list.extend( [self.zerostr]*(L_temp_LR_seq - len(SR_seq_list)))
        SR_idx_seq_list.extend([self.zerostr]*(L_temp_LR_seq - len(SR_idx_seq_list)))
        SR_del_seq_list.extend([self.zerostr]*(L_temp_LR_seq - len(SR_del_seq_list)))
###############

        all_seq_idx_list.append([SR_seq_list, SR_idx_seq_list, n_rep])
        all_del_seq_list.append([SR_del_seq_list, n_rep])

#########################################################################################################

    # Sort the correction points based on position
    crt_pt_sorted_array = sorted(list(crt_pt_ls))
    #crt_pt_sorted_array = numpy.array(numpy.sort(list(crt_pt_ls)))

    
    #temp_index_ls = numpy.searchsorted(crt_pt_sorted_array,[start_pt,end_pt])
    temp_index_ls_spread =  [x for x in range(len(crt_pt_sorted_array)) if crt_pt_sorted_array[x] >= start_pt and crt_pt_sorted_array[x] < end_pt]
    if len(temp_index_ls_spread) == 0:
      temp_index_ls = [0,0]
    else:
      temp_index_ls = [temp_index_ls_spread[0],temp_index_ls_spread[-1]+1] #get the first and last elements, but add one to the last element.
    crt_repos_ls = [x - start_pt for x in crt_pt_sorted_array[temp_index_ls[0]:temp_index_ls[1]]]
    temp_LR_seq_list = list(temp_LR_seq)
    i = 0
    # Compute coverage information for the long read
    for x in temp_LR_seq_list:
        n = int(temp_LR_idx_seq_list[i])
        temp_LR_seq_list[i] = x*n
        coverage_list[i] = coverage_list[i] * n
        i+=1

    # Make the corrections (+,>,HC)
    for crt_repos in crt_repos_ls:
        temp_candidate_ls = []
        # For each SR
        for temp_SR_seq_idx_list in all_seq_idx_list: # list(list(list()))

            x = temp_SR_seq_idx_list[0][crt_repos] # base
            n = int(temp_SR_seq_idx_list[1][crt_repos]) # repeat of the base
            n_rep =int( temp_SR_seq_idx_list[2]) # repeat of the short read
            
            pre_x = temp_SR_seq_idx_list[0][max(0,crt_repos-1)]
            post_x = temp_SR_seq_idx_list[0][min(len(temp_SR_seq_idx_list[0])-1, crt_repos+1)]
            if n>0 and x!='N' and pre_x!='N' and post_x!='N':
                temp_candidate_ls.extend([x*n]*n_rep)
        [optimal_seq, n_max] = optimize_seq(temp_candidate_ls)

        if optimal_seq!='':
            if optimal_seq=='-':
                optimal_seq=''
            temp_LR_seq_list[crt_repos] = optimal_seq
            coverage_list[crt_repos] =  fq_char_list[min( n_max, NUM_FQ_CHAR)] * len(optimal_seq)

#########################################################################################################

    coverage_L = len(temp_LR_seq_list)

#########################################################################################################

    #del_pt_sorted_array = numpy.array(numpy.sort(list(del_pt_set)))
    #temp_del_index_ls = numpy.searchsorted(del_pt_sorted_array,[start_pt-1,end_pt])
    #del_repos_ls = del_pt_sorted_array[temp_del_index_ls[0]:temp_index_ls[1]] - start_pt -2

    del_pt_sorted_array = sorted(list(del_pt_set))
    temp_del_index_ls_spread =  [x for x in range(len(del_pt_sorted_array)) if del_pt_sorted_array[x] >= start_pt-1 and del_pt_sorted_array[x] < end_pt]
    if len(temp_del_index_ls_spread)==0:
      temp_del_index_ls = [0,0]
    else: 
      temp_del_index_ls = [temp_del_index_ls_spread[0],temp_del_index_ls_spread[-1]+1] #get the first and last elements, but add one to the last element.
    ##### is this a bug here? it seems the points we slice between aren't correct
    # I am leaving it as it was. It doesn't look like it changes much on how the code executes.
    del_repos_ls = [x - start_pt -2 for x in del_pt_sorted_array[temp_del_index_ls[0]:temp_index_ls[1]]]
    #del_repos_ls = [x - start_pt -2 for x in del_pt_sorted_array[temp_del_index_ls[0]:temp_del_index_ls[1]]]

    Npredel=0
    # Make the corrections (-)
    for del_repos in del_repos_ls:
        temp_candidate_ls = []
        # For each SR
        for SR_del_seq_list_ls in all_del_seq_list:
            SR_del_seq_list = SR_del_seq_list_ls[0]
            n_rep = SR_del_seq_list_ls[1]
            if not SR_del_seq_list[del_repos] == '0':
                temp_candidate_ls.extend([SR_del_seq_list[del_repos]]*n_rep)
        [optimal_seq, n_max] = optimize_seq(temp_candidate_ls)

        if optimal_seq!='' and optimal_seq!='=':
            del_repos_Npredel_1 = del_repos+Npredel+1
            temp_LR_seq_list.insert(del_repos_Npredel_1, optimal_seq)
            coverage_list.insert(del_repos_Npredel_1, fq_char_list[min( n_max, NUM_FQ_CHAR)] * len(optimal_seq))
            coverage_L +=1
            Npredel+=1
#########################################################################################################

    final_seq = ''.join(temp_LR_seq_list[1:(coverage_L-1)]) # create the corrected long read, Note: the end and start pos of SRs are not used for correction
    coverage_seq = ''.join(coverage_list[1:(coverage_L-1)]) # Coverage data, turns into quality in the output fastq
    
#########################################################################################################
    
    output['full_fasta'] =  '>' + self.LR_read_name_list[read_int]+"\n"
    output['full_fasta'] += five_end_seq + final_seq.replace('X','').replace('Z','') + three_end_seq + "\n"

    corrected_seq = final_seq.replace('X','').replace('Z','')
    coverage = 1. * sum((cvrg != fq_char_list[0]) for cvrg in coverage_seq) / len(corrected_seq)

    output['corrected_fasta']  = '>' + self.LR_read_name_list[read_int] + '|' + "{0:.2f}".format(round(coverage, 2)) + "\n"
    output['corrected_fasta'] += corrected_seq + "\n"
    
    output['corrected_fastq']  = '@' + self.LR_read_name_list[read_int] + '|' + "{0:.2f}".format(round(coverage, 2)) + "\n"
    output['corrected_fastq'] += corrected_seq + "\n"
    output['corrected_fastq'] += "+\n"
    output['corrected_fastq'] += coverage_seq.replace('X','').replace('Z','') + "\n"
    return output
