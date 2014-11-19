import sqlite3

c = sqlite3.connect('ref_des.db')

rows = list(c.execute('select distinct array_code,site_prefix,site_suffix,node_type_code,node_site_seq,latitude,longitude from ooi_instruments;'))
for row in rows:
    array_code = row[0]
    site_prefix = row[1]
    site_suffix = row[2]
    node_type_code = row[3]
    node_site_seq = row[4]
    lat = row[5]
    lon = row[6]

    ref_des = array_code + site_prefix + site_suffix + '-' + node_type_code + node_site_seq.zfill(3)
    port_number = '00'
    instrument_class = 'ENG00'
    instrument_series = '0'
    instrument_seq = '000'
    eng_suffix = '00-ENG00000'
    ref_des = ''.join([
        array_code,
        site_prefix,
        site_suffix,
        '-',
        node_type_code,
        node_site_seq.zfill(3),
        '-',
        port_number,
        '-',
        instrument_class,
        instrument_series,
        instrument_seq])
    print ref_des
    c.execute('INSERT INTO ooi_instruments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
        ref_des, 
        array_code, 
        site_prefix,
        site_suffix,
        node_type_code,
        node_site_seq,
        port_number,
        instrument_class,
        instrument_series,
        instrument_seq,
        lat,
        lon))
c.commit()
