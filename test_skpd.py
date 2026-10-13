import requests, json, bs4

def test_skpd():
    c = json.load(open('auth.json'))['cookies']
    cookies = {k['name']:k['value'] for k in c}
    h = {'User-Agent':'Mozilla/5.0'}
    
    res = requests.get('https://spot.tangerangkab.go.id/utilitas/kehadiran/shift', cookies=cookies, headers=h)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    
    def get_val(sel_id):
        sel = soup.find(id=sel_id)
        if not sel: return ''
        opt = sel.find('option', selected=True)
        if opt: return opt.get('value', '')
        opt2 = sel.find('option')
        if opt2: return opt2.get('value', '')
        return ''
        
    skpd = {
        'kunkom_scr': get_val('kunkom_scr'),
        'kununit_scr': get_val('kununit_scr'),
        'unit1_scr': get_val('unit1_scr'),
        'unit2_scr': get_val('unit2_scr'),
        'unit3_scr': get_val('unit3_scr'),
        'unit4_scr': get_val('unit4_scr')
    }
    
    print("Extracted SKPD:", skpd)
    
    payload = {
        'kunkom': skpd['kunkom_scr'],
        'kununit': skpd['kununit_scr'],
        'unit1': skpd['unit1_scr'],
        'unit2': skpd['unit2_scr'],
        'unit3': skpd['unit3_scr'],
        'unit4': skpd['unit4_scr'],
        'status': '1', 
        'tgl': 'March 2026',
        'nama': '197402102025211014', 
        'display': '10'
    }
    
    print("Payload sent to pagging:", payload)
    r = requests.post('https://spot.tangerangkab.go.id/utilitas/kehadiran/shift/pagging/0', data=payload, cookies=cookies, headers=h)
    print("Response Length:", len(r.text))
    print("Is SAHRONI found:", '197402' in r.text or 'SAHRONI' in r.text)
    
if __name__ == '__main__':
    test_skpd()
