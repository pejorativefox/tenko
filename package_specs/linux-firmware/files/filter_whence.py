import os, sys
keep_dirs = set('''amdgpu amdnpu radeon i915 xe nvidia rtl_bt rtlwifi rtw88 rtw89 rtl_nic mediatek aic ar3k ath10k ath11k ath12k ath6k ath9k_htc qca brcm cypress intel amd amdtee amd-ucode libertas nxp ti-connectivity mwl8k mwlwifi rsi wfx wilc1000 zd1211 zd1201 atmel airoha b43 b43legacy b43-open'''.split())
def kept(p):
    p = p.strip().strip('"')
    if p.startswith('./'): p = p[2:]
    if not p: return False
    if '/' not in p: return True          # top-level firmware file
    return p.split('/',1)[0] in keep_dirs
out=[]
for line in open('WHENCE', encoding='utf-8', errors='replace'):
    if line.startswith(('File:','RawFile:')):
        p=line.split(':',1)[1].strip().strip('"')
        if kept(p): out.append(line)
    elif line.startswith('Link:'):
        rest=line.split(':',1)[1].strip()
        if '->' not in rest: continue
        l,t=[x.strip().strip('"') for x in rest.split('->',1)]
        # normalize the target relative to the link's directory
        base=os.path.dirname(l)
        tp=os.path.normpath(os.path.join(base,t)) if base else os.path.normpath(t)
        if kept(l) and kept(tp):
            out.append(line)
open('WHENCE.filtered','w').write(''.join(out))
print('kept lines:', len(out), file=sys.stderr)
