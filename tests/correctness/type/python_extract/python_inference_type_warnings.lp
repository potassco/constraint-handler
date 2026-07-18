phase_request(type_check,true).

variable_define(extract_list,operation(pythonExtract("tmp=[1,2,3]","tmp"),())).

variable_define(extract_obj,operation(pythonExtract("tmp=object()","tmp"),())).
