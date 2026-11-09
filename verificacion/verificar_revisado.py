"""Bind revised numeric claims to their quantities, preserving the legacy checker."""
import json
import pathlib
import re
import sys

import verificar_legacy as legacy

V=pathlib.Path(__file__).resolve().parent
S=json.loads((V.parent/'auditoria/ROBUSTNESS_RESULTS.json').read_text())
es=legacy.es
ci=S['supplier_cluster_bootstrap']['post_ci95']
delta_ci=S['supplier_cluster_bootstrap']['paired_post_minus_pre_ci95']
supplier=S['leave_one_supplier_Bpost_range'];years=list(S['leave_one_year_Bpost'].values())
legacy.CLAIMS=[(name,es(ci[0]) if name=='B_post_ic0' else es(ci[1]) if name=='B_post_ic1' else literal,ok)
               for name,literal,ok in legacy.CLAIMS]
new_values=[S['observed']['post_minus_pre'],*delta_ci,*supplier,min(years),max(years)]
legacy.CLAIMS += [(f'robustness_{i}',es(value),True) for i,value in enumerate(new_values)]
legacy.CLAIMS += [('supplier_clusters',es(S['supplier_cluster_bootstrap']['supplier_clusters'],0),True),
                  ('cluster_replicates',es(S['supplier_cluster_bootstrap']['replicates'],0),True),
                  ('cluster_seed',str(S['supplier_cluster_bootstrap']['seed']),True)]
SEMANTIC={
 'post_B':f"vale **{es(S['observed']['services_post_B18150'])}**.",
 'cluster_interval':f"el intervalo de sensibilidad del 95 % va de **{es(ci[0])} a {es(ci[1])}**.",
 'leave_supplier':f"al omitir un proveedor cada vez: la razón queda entre {es(supplier[0])} y {es(supplier[1])}.",
 'leave_year':f"Al omitir un año, entre {es(min(years))} y {es(max(years))}.",
 'paired_difference':f"La diferencia entre estas dos razones es de {es(S['observed']['post_minus_pre'])} puntos; su intervalo de sensibilidad, conservando juntas las líneas de cada proveedor antes y después, va de {es(delta_ci[0])} a {es(delta_ci[1])}.",
 'replicates_seed':f"en {es(S['supplier_cluster_bootstrap']['replicates'],0)} remuestreos, con semilla {S['supplier_cluster_bootstrap']['seed']}.",
 'cluster_count':f"Se agruparon {es(S['supplier_cluster_bootstrap']['supplier_clusters'],0)} nombres normalizados de proveedor;"
}


def verificar(text):
    failures=legacy.verificar(text)
    return failures+['ASOCIACION '+key for key,clause in SEMANTIC.items() if clause not in text]


def targeted_mutations(text):
    changes=[('post_B',es(S['observed']['services_post_B18150']),es(legacy.R['E1_E2_dfb_servicios']['PRE_21780']['B'])),
             ('cluster_interval',es(ci[0]),es(ci[1])),('cluster_interval',es(ci[1]),es(ci[0])),
             ('leave_supplier',es(supplier[0]),es(supplier[1])),('leave_year',es(min(years)),es(max(years))),
             ('paired_difference',es(delta_ci[0]),es(delta_ci[1])),
             ('cluster_count',es(S['supplier_cluster_bootstrap']['supplier_clusters'],0),es(S['supplier_cluster_bootstrap']['replicates'],0))]
    detected=0;legacy_detected=0
    for key,old,new in changes:
        clause=SEMANTIC[key];first=text.index(clause)+clause.index(old)
        choices=[m.start() for m in re.finditer(r'(?<![\d.,])'+re.escape(new)+r'(?!\d|[.,]\d)',text)]
        second=next(pos for pos in choices if pos!=first)
        edits=sorted([(first,len(old),new),(second,len(new),old)],reverse=True)
        mutated=text
        for pos,length,value in edits:mutated=mutated[:pos]+value+mutated[pos+length:]
        assert mutated!=text
        detected+=bool(verificar(mutated));legacy_detected+=bool(legacy.verificar(mutated))
    assert detected==len(changes),'A revised claim mutation escaped its binding check'
    return {'targeted_cases':len(changes),'type':'Swap two already-valid numbers, preserving their global presence',
            'detected':detected,'legacy_global_literal_detected':legacy_detected,
            'scope':'Targeted revised clauses only; not a general detection benchmark or verification of every historical sentence'}


def main():
    path=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else legacy.ART
    text=path.read_text(encoding='utf-8');failures=verificar(text)
    result={'numeric_source_checks':len(legacy.CLAIMS),'revised_clause_bindings':len(SEMANTIC),'failures':failures,
            'targeted_mutations':targeted_mutations(text) if not failures else None}
    (V/'STATEMENT_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));raise SystemExit(bool(failures))


if __name__=='__main__':main()
