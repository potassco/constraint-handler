#include "includeAll.lp".

%%% ensure X  means X has to have value true

%%% usc_a1: a1 = true
%%% usc_a2: a2 = true
%%% usc_ad: ad = a1 | a2
%%% usc_ae: ensure \lnot ad

%%% usc_c1: c1 = true
%%% usc_c2: c2 = choose true or false
%%% usc_ce1: ensure c1 <-> c2
%%% usc_ce2: ensure \lnot c2

%%% usc_d(1): d(1) = true
%%% usc_d(2): d(2) = true
%%% usc_dd: dd = d(1) | d(2)
%%% usc_de: ensure default(\lnot dd, true)

%%% usc_ba: b(1) = true
%%% usc_ba: b(2) = true
%%% usc_bd: bd = b(1) | b(2)
%%% usc_be: ensure default(\lnot bd, true)

%%% usc_e1: e1 = guess true or false
%%% usc_e2: e2 = guess true or false
%%% usc_ec: ec = e1 & e2
%%% usc_ed: ed = e1 | e2
%%% usc_ee: ensure ec <-> ed

%%% cores:
%%% [usc_ae]
%%% [usc_ce1, usc_ce2]
%%% [usc_dd, usc_d(1), usc_de]
%%% [usc_dd, usc_d(2), usc_de]


variable_define(usc_a1,a1,val(bool,true)).
variable_define(usc_a2,a2,val(bool,true)).
variable_define(usc_ad,ad,operation(disj,(variable(a1),(variable(a2),())))).
ensure(usc_ae,operation(lnot,(variable(ad),()))).

variable_define(usc_c1,c1,val(bool,(true))).
variable_declare(usc_c2,c2,boolDomain).
ensure(usc_ce1,operation(leqv,(variable(c1),(variable(c2),())))).
ensure(usc_ce2,operation(lnot,(variable(c2),()))).

variable_define(usc_d(1),d(1),val(bool,true)).
variable_define(usc_d(2),d(2),val(bool,true)).
variable_define(usc_dd,dd,operation(disj,(variable(d(1)),(variable(d(2)),())))).
ensure(usc_de,operation(default,
                       (operation(lnot,(variable(dd),())),
                       (val(bool,true),())))).

variable_define(usc_ba,b(1),val(bool,true)).
variable_define(usc_ba,b(2),val(bool,true)).
variable_define(usc_bd,bd,operation(disj,(variable(b(1)),(variable(b(2)),())))).
ensure(usc_be,operation(default,
                       (operation(lnot,(variable(bd),())),
                       (val(bool,true),())))).

variable_declare(usc_e1,e1,boolDomain).
variable_declare(usc_e2,e2,boolDomain).
variable_define(usc_ec,ec,operation(conj,(variable(e1),(variable(e2),())))).
variable_define(usc_ed,ed,operation(disj,(variable(e1),(variable(e2),())))).
ensure(usc_ee,operation(leqv,(variable(ec),(variable(ed),())))).

#show value/3.
#show usc_active/1.
#script (python)

import constraint_handler.unsatCoreSupport as ch_usc

#def main(prg):
#    prg.ground()
#    assMap = ch_usc.get_assumptions(prg)
#    symbs = [str(f) for f in assMap.values() if len(f.name) == 6]
#    keys = [k for k,f in assMap.items() if len(f.name) == 6]
#    print(symbs)
#    print(assMap)
#    ch_usc.relax(prg,assMap.values())
#    #ch_usc.relax(prg,symbs)
#    print(assMap)
#    for core in ch_usc.enumerate_mus(prg,assMap.keys()):
#    #for core in ch_usc.enumerate_mus(prg,keys):
#        core_assumptions = [assMap[a] for a in core]
#        print("found core: ",[str(a) for a in core_assumptions])

def main(prg):
    prg.ground()
    assumptionMap = ch_usc.get_assumptions(prg)
    ch_usc.relax(prg,assumptionMap.values())
    readable = { key : str(val) for key,val in assumptionMap.items() }
#    print(readable)
#    ch_usc.relax(prg,[clingo.Function("usc_ae",[]),clingo.Function("usc_a2",[])])
#    assert False
    for core in ch_usc.enumerate_mus(prg,assumptionMap.keys()):
        print("found core: ",[readable[a] for a in core])
    prg.solve()

#def main(prg):
#    prg.ground()
#    prg.solve()

#end.
