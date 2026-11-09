"""Exploratory independent audit; raw supplier names never leave memory."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
ORIGINAL=ROOT.parent


def ratio(numerator,reference):
    return float(4*numerator/reference) if reference else None


def bootstrap(counts,reps=10000,seed=20261109):
    rng=np.random.default_rng(seed);n=len(counts);values=[];unsupported=0
    for start in range(0,reps,128):
        indices=rng.integers(0,n,size=(min(128,reps-start),n))
        sums=counts[indices].sum(axis=1)
        valid=(sums[:,1]>0)&(sums[:,3]>0);unsupported+=int((~valid).sum())
        pre=4*sums[valid,0]/sums[valid,1];post=4*sums[valid,2]/sums[valid,3]
        values.append(np.column_stack([pre,post,post-pre]))
    x=np.concatenate(values)
    assert unsupported/reps<.01,'Too many unsupported bootstrap samples'
    return {'pre_ci95':np.percentile(x[:,0],[2.5,97.5]).tolist(),
            'post_ci95':np.percentile(x[:,1],[2.5,97.5]).tolist(),
            'paired_post_minus_pre_ci95':np.percentile(x[:,2],[2.5,97.5]).tolist(),
            'replicates':reps,'seed':seed,'unsupported_replicates':unsupported,'supplier_clusters':n}


def read_archive():
    records=[json.loads(line) for line in (ORIGINAL/'datos/manifest.jsonl').read_text(encoding='utf-8').splitlines()]
    records=[r for r in records if r['dataset']=='contratos-menores']
    selected={};ties=0
    for record in records:
        path=(ORIGINAL/'datos/raw/contratos-menores'/f"{record['resource_id']}.csv").resolve()
        path.relative_to(ORIGINAL.resolve())
        assert path.stat().st_size==record['bytes']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'],'Raw archive hash mismatch'
        for encoding in ['utf-8-sig','cp1252']:
            try:frame=pd.read_csv(path,sep=';',encoding=encoding,dtype=str,on_bad_lines='error');break
            except UnicodeDecodeError:continue
        else:raise AssertionError('Unknown source encoding')
        frame=frame.loc[:,~frame.columns.str.startswith('Unnamed')]
        frame.columns=[c.split('/')[-1].strip() for c in frame.columns]
        assert frame['EJERCICIO'].nunique(dropna=False)==frame['MES HASTA'].nunique(dropna=False)==1
        year,month=int(frame['EJERCICIO'].iloc[0]),int(frame['MES HASTA'].iloc[0])
        assert 1<=month<=12
        if year not in selected or month>selected[year][0]:selected[year]=(month,frame)
        elif month==selected[year][0]:
            assert frame.equals(selected[year][1]),'Conflicting duplicate latest cut'
            ties+=1
    result=pd.concat([f for m,f in selected.values()],ignore_index=True)
    result['ej']=pd.to_numeric(result['EJERCICIO']).astype(int)
    text=result['OBLIGACION'].str.replace('.','',regex=False).str.replace(',','.',regex=False)
    result['amount']=pd.to_numeric(text,errors='raise');assert np.isfinite(result.amount).all()
    return result,{'raw_files_verified':len(records),'duplicate_identical_latest_cuts':ties,
                   'selected_cuts':{y:m for y,(m,f) in sorted(selected.items())},'selected_rows_including_partial2026':len(result)}


def main():
    assert ratio(3,2)==6 and ratio(1,0) is None
    constant=bootstrap(np.array([[1,2,4,2]]*5),reps=100,seed=9)
    assert constant['paired_post_minus_pre_ci95']==[6.0,6.0]
    frame,provenance=read_archive()
    services=frame[frame['MODELO ADMIN DESCRIPCION'].str.contains('de servicios',case=False,na=False)].copy()
    services=services[services.ej.isin(list(range(2014,2018))+list(range(2019,2026)))].copy()
    vendor=services['PERSONA ADJUDICATARIA'].str.strip().str.upper()
    missing=vendor.isna()|vendor.eq('')
    vendor=vendor.mask(missing,pd.Series(['__MISSING_ROW_'+str(i) for i in services.index],index=services.index))
    services['supplier_cluster']=vendor
    pre=services.ej.between(2014,2017);post=services.ej.between(2019,2025)
    band=services.amount.between(.97*18150,18150)
    reference=(services.amount>=.85*18150)&(services.amount<.97*18150)
    for name,indicator in [('pre_band',pre&band),('pre_ref',pre&reference),('post_band',post&band),('post_ref',post&reference)]:
        services[name]=indicator.astype(int)
    counts=services.groupby('supplier_cluster',sort=True)[['pre_band','pre_ref','post_band','post_ref']].sum().to_numpy()
    totals=counts.sum(0);pre_b=ratio(*totals[:2]);post_b=ratio(*totals[2:])
    assert totals.tolist()==[100,167,1119,553]
    assert round(post_b,2)==8.09 and round(pre_b,2)==2.40
    post_frame=services.loc[post]
    below=int(((post_frame.amount>18150-500)&(post_frame.amount<=18150)).sum())
    above=int(((post_frame.amount>18150)&(post_frame.amount<=18150+500)).sum())
    assert (below,above)==(1105,0)
    boot=bootstrap(counts)
    leave_supplier=[ratio(totals[2]-row[2],totals[3]-row[3]) for row in counts]
    assert all(v is not None for v in leave_supplier)
    leave_year={}
    for year in range(2019,2026):
        x=post_frame[post_frame.ej!=year]
        leave_year[year]=ratio(int(x.post_band.sum()),int(x.post_ref.sum()))
    all_post=frame[frame.ej.between(2019,2025)]
    ids=all_post.groupby(['ej','EXPEDIENTE CONTABLE'],dropna=False).size()
    old_upper=post_frame.amount.between(.97*21780,21780)
    old_reference=(post_frame.amount>=.85*21780)&(post_frame.amount<.97*21780)
    result={'role':'Exploratory sensitivity, not independent confirmation or causal/legality proof',
            'provenance':provenance,'observed':{'services_pre_B18150':pre_b,'services_post_B18150':post_b,
            'post_minus_pre':post_b-pre_b,'counts_pre_band_ref_post_band_ref':totals.tolist(),
            'services_500eur_below':below,'services_500eur_above':above,
            'old_upper_post_B21780':ratio(int(old_upper.sum()),int(old_reference.sum())),
            'old_upper_post_band':int(old_upper.sum()),'old_upper_post_reference':int(old_reference.sum())},
            'supplier_cluster_bootstrap':boot,'missing_supplier_rows_separate_clusters':int(missing.sum()),
            'leave_one_supplier_Bpost_range':[min(leave_supplier),max(leave_supplier)],'leave_one_year_Bpost':leave_year,
            'accounting_unit':{'post_lines':len(all_post),'distinct_exercise_accounting_identifiers':len(ids),
                               'identifiers_with_multiple_lines':int((ids>1).sum()),'maximum_lines_per_identifier':int(ids.max())},
            'privacy':{'supplier_names_exported':False,'raw_rows_exported':False},
            'uncertainty':'Observed census counts are exact for this archived scope. Bootstrap intervals depend on a hypothetical supplier-resampling model and imperfect name identities. No untreated comparison group.'}
    (ROOT/'ROBUSTNESS_RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'raw_files_verified':provenance['raw_files_verified'],'rows':provenance['selected_rows_including_partial2026'],
                      'post_B':post_b,'cluster_ci95':boot['post_ci95'],'paired_difference_ci95':boot['paired_post_minus_pre_ci95'],
                      'leave_supplier_range':result['leave_one_supplier_Bpost_range'],'names_exported':False}))


if __name__=='__main__':main()
