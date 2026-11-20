import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import numpy as np
from PIL import Image, PngImagePlugin
import pytest
from scripts.build_cxr_fixture import build
from src.cxr_manifest import audit, COLUMNS, inspect_image

@pytest.fixture
def fixture(tmp_path):
    build(tmp_path)
    return tmp_path

def rows(root):
    with (root/'manifest.csv').open() as f:return list(csv.DictReader(f))

def write_rows(root, values):
    with (root/'manifest.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNS,lineterminator='\n');writer.writeheader();writer.writerows(values)

def run(root):return audit(root/'manifest.csv',root/'source.json',root)
def codes(report):return {i['code'] for i in report['issues']}

def test_valid_deterministic_fixture_and_unchanged_inputs(fixture):
    before={p.name:p.read_bytes() for p in fixture.iterdir()}
    a=run(fixture);assert a==run(fixture);assert a['passed'];assert a['decoded_images']==3
    assert a['data_kind']=='synthetic';assert a['training_readiness']=='not_assessed'
    assert [(i['width'],i['height'],i['minimum'],i['maximum']) for i in a['images']]==[(16,12,0,191),(16,12,1,255),(16,12,0,255)]
    assert before=={p.name:p.read_bytes() for p in fixture.iterdir()}
    assert a['split_label_counts']['test']['uncertain']==1
    assert a['split_label_counts']['test']['negative']==0

@pytest.mark.parametrize('key,code',[('patient_id','patient_id_cross_split_leakage'),('study_id','study_id_cross_split_leakage'),('image_id','duplicate_image_id')])
def test_cross_split_identifier_leakage(fixture,key,code):
    values=rows(fixture);values[1][key]=values[0][key];write_rows(fixture,values)
    report=run(fixture);assert not report['passed'];assert code in codes(report)

def test_study_cannot_belong_to_two_patients_even_within_split(fixture):
    values=rows(fixture);values[1]['study_id']=values[0]['study_id'];values[1]['split']='train';write_rows(fixture,values)
    assert 'study_assigned_to_multiple_patients' in codes(run(fixture))

def test_multiple_distinct_views_same_patient_and_study_within_split_allowed(fixture):
    values=rows(fixture);values[1].update(patient_id=values[0]['patient_id'],study_id=values[0]['study_id'],split='train',label=values[0]['label']);write_rows(fixture,values)
    assert run(fixture)['passed']

def test_duplicate_bytes_under_different_names_and_ids(fixture):
    shutil.copyfile(fixture/'fixture-0.png',fixture/'fixture-1.png')
    report=run(fixture);assert not report['passed'];assert {'duplicate_file','duplicate_pixel'}<=codes(report)

def test_reencoded_pixels_detected_without_file_hash_match(fixture):
    with Image.open(fixture/'fixture-0.png') as image:
        extra=PngImagePlugin.PngInfo();extra.add_text('synthetic','different PNG encoding')
        image.save(fixture/'fixture-1.png',compress_level=0,pnginfo=extra)
    report=run(fixture);assert 'duplicate_pixel' in codes(report);assert 'duplicate_file' not in codes(report)

@pytest.mark.parametrize('relative',['../outside.png','/tmp/outside.png','C:/outside.png','sub\\file.png','./fixture-0.png','missing.png'])
def test_invalid_missing_and_traversal_paths_fail_closed(fixture,relative):
    values=rows(fixture);values[0]['path']=relative;write_rows(fixture,values)
    assert 'unreadable_unsupported_or_outside_root_image' in codes(run(fixture))

def test_symlink_outside_root_rejected(fixture,tmp_path):
    outside=tmp_path.parent/(tmp_path.name+'-outside.png');shutil.copyfile(fixture/'fixture-0.png',outside)
    try:
        (fixture/'link.png').symlink_to(outside)
        values=rows(fixture);values[0]['path']='link.png';write_rows(fixture,values)
        assert not run(fixture)['passed']
    finally:outside.unlink()

@pytest.mark.parametrize('kind',['corrupt','rgb','oversized','truncated'])
def test_unsupported_or_broken_images(fixture,kind):
    path=fixture/'fixture-0.png'
    if kind=='corrupt':path.write_bytes(b'not an image')
    if kind=='rgb':Image.new('RGB',(16,12)).save(path)
    if kind=='truncated':path.write_bytes(path.read_bytes()[:40])
    report=audit(fixture/'manifest.csv',fixture/'source.json',fixture,max_pixels=10 if kind=='oversized' else 10000)
    assert not report['passed']

def test_uint16_jpeg_and_constant_quality_flag(fixture):
    path=fixture/'sixteen.png';pixels=np.arange(192,dtype=np.uint16).reshape(12,16)*300;Image.fromarray(pixels).save(path)
    result=inspect_image(path,10000,100000);assert result['maximum']==57300;assert result['minimum']==0
    jpeg=fixture/'gray.jpg';Image.fromarray(np.arange(192,dtype=np.uint8).reshape(12,16)).save(jpeg)
    assert inspect_image(jpeg,10000,100000)['width']==16
    Image.new('L',(16,12),3).save(fixture/'fixture-0.png')
    report=run(fixture);assert report['passed'];assert report['quality_warnings']==[{'code':'constant_image','rows':[2]}]

@pytest.mark.parametrize('key,value',[('split','holdout'),('view','frontal'),('label',''),('label','-1'),('patient_id','patient with spaces')])
def test_schema_and_explicit_label_states(fixture,key,value):
    values=rows(fixture);values[0][key]=value;write_rows(fixture,values);assert not run(fixture)['passed']

def test_missing_label_is_not_negative(fixture):
    values=rows(fixture);values[0]['label']='missing';write_rows(fixture,values)
    report=run(fixture);assert report['passed'];assert report['split_label_counts']['train']['missing']==1;assert report['split_label_counts']['train']['negative']==0

@pytest.mark.parametrize('text',['image_id,path\n',','.join(COLUMNS)+'\n',','.join(COLUMNS)+',image_id\n'])
def test_bad_headers_or_empty_manifest_raise(fixture,text):
    (fixture/'manifest.csv').write_text(text)
    with pytest.raises(ValueError):run(fixture)

def test_provenance_and_limits_fail_closed(fixture):
    source=json.loads((fixture/'source.json').read_text());del source['version'];(fixture/'source.json').write_text(json.dumps(source))
    with pytest.raises(ValueError):run(fixture)
    build(fixture)
    for limits in [dict(max_pixels=0),dict(max_bytes=True)]:
        with pytest.raises(ValueError):audit(fixture/'manifest.csv',fixture/'source.json',fixture,**limits)
    assert not audit(fixture/'manifest.csv',fixture/'source.json',fixture,max_bytes=1)['passed']
    (fixture/'source.json').write_text('{"dataset_id":"a","dataset_id":"b"}')
    with pytest.raises(ValueError):run(fixture)

def test_report_does_not_expose_patient_study_or_paths(fixture):
    values=rows(fixture);values[0].update(patient_id='private-patient',study_id='private-study',path='../private-image.png');values[1]['patient_id']='private-patient';write_rows(fixture,values)
    encoded=json.dumps(run(fixture));assert all(s not in encoded for s in ['private-patient','private-study','private-image.png',str(fixture)])

def test_cli_success_leakage_and_schema_exit_codes(fixture):
    command=[sys.executable,'-m','src.cxr_manifest',str(fixture/'manifest.csv'),'--source',str(fixture/'source.json'),'--data-root',str(fixture)]
    good=subprocess.run(command,capture_output=True,text=True);assert good.returncode==0;assert json.loads(good.stdout)['passed']
    values=rows(fixture);values[1]['patient_id']=values[0]['patient_id'];write_rows(fixture,values)
    bad=subprocess.run(command,capture_output=True,text=True);assert bad.returncode==1;assert not json.loads(bad.stdout)['passed']
    (fixture/'manifest.csv').write_text('bad header\n')
    invalid=subprocess.run(command,capture_output=True,text=True);assert invalid.returncode==2;assert not invalid.stdout;assert 'no identifiers' in invalid.stderr

@pytest.mark.parametrize('labels,conflict', [
    (('positive','negative'),True), (('negative','positive'),True),
    (('positive','uncertain'),False), (('negative','missing'),False),
    (('uncertain','missing'),False), (('positive','positive'),False)])
def test_study_label_consistency_preserves_unknown_states(fixture,labels,conflict):
    values=rows(fixture)
    values[1].update(patient_id=values[0]['patient_id'],study_id=values[0]['study_id'],split='train')
    for row,label in zip(values,labels):row['label']=label
    write_rows(fixture,values)
    report=run(fixture)
    assert ('study_conflicting_definitive_labels' in codes(report)) == conflict
    assert report['passed'] == (not conflict)
    if conflict:
        assert {'code':'study_conflicting_definitive_labels','rows':[2,3]} in report['issues']
    else:
        for label in labels:assert report['split_label_counts']['train'][label] >= 1

def test_different_studies_same_patient_may_have_different_labels(fixture):
    values=rows(fixture);values[1].update(patient_id=values[0]['patient_id'],split='train')
    values[0]['label']='positive';values[1]['label']='negative';write_rows(fixture,values)
    assert run(fixture)['passed']
