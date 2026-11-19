"""Generate original geometric grayscale fixtures, not radiographs or patient data."""
import argparse,csv,json
from pathlib import Path
from PIL import Image
import numpy as np

def build(root):
    root.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i,split in enumerate(('train','validation','test')):
        # Different gradients prevent accidental decoded-pixel duplicates.
        pixels=((np.arange(192).reshape(12,16)*(i+1)+i*23)%256).astype('uint8')
        name=f'fixture-{i}.png';Image.fromarray(pixels).save(root/name)
        rows.append([f'image-{i}',f'patient-{i}',f'study-{i}',name,split,('PA','AP','UNKNOWN')[i],('negative','positive','uncertain')[i]])
    with (root/'manifest.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['image_id','patient_id','study_id','path','split','view','label']);w.writerows(rows)
    meta=dict(dataset_id='synthetic-cxr-manifest-fixture',version='1',source_url='https://github.com/hrix7/Medical-Imaging-Deep-Learning',license='Original generated geometric test fixtures; no patient data',data_kind='synthetic',target_name='synthetic_example_finding')
    (root/'source.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);build(p.parse_args().output)
