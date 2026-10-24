"""Fetch FMI's CAP warning feed and write a compact warnings.json for the app.

The feed itself can't be read from a browser (no CORS header), so a scheduled GitHub
Action runs this and publishes the result next to index.html. Standard library only.

Usage: python build_warnings.py OUT.json [feed.xml]
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEED = 'https://alerts.fmi.fi/cap/feed/atom_fi-FI.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'c': 'urn:oasis:names:tc:emergency:cap:1.2'}
MAX_POINTS = 250  # per polygon; plenty for point-in-polygon at town scale


def simplify(text):
    pts = []
    for pair in text.split():
        lat, lon = (round(float(v), 3) for v in pair.split(','))
        if not pts or pts[-1] != [lat, lon]:
            pts.append([lat, lon])
    if len(pts) > MAX_POINTS:
        step = -(-len(pts) // MAX_POINTS)
        pts = pts[::step]
    return pts


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    now = datetime.now(timezone.utc)
    out = []
    for entry in root.findall('a:entry', NS):
        alert = entry.find('a:content/c:alert', NS)
        if alert is None or alert.findtext('c:msgType', namespaces=NS) == 'Cancel':
            continue
        info = next((i for i in alert.findall('c:info', NS)
                     if i.findtext('c:language', namespaces=NS) == 'fi-FI'), None)
        if info is None:
            continue
        expires = info.findtext('c:expires', namespaces=NS)
        if expires and datetime.fromisoformat(expires) < now:
            continue
        params = {p.findtext('c:valueName', namespaces=NS): p.findtext('c:value', namespaces=NS)
                  for p in info.findall('c:parameter', NS)}
        out.append({
            'id': alert.findtext('c:identifier', namespaces=NS),
            'type': info.findtext('c:eventCode/c:value', namespaces=NS),
            'event': info.findtext('c:event', namespaces=NS),
            'color': params.get('color', 'yellow'),
            'headline': info.findtext('c:headline', namespaces=NS),
            'description': info.findtext('c:description', namespaces=NS),
            'impacts': params.get('typicalImpacts'),
            'onset': info.findtext('c:onset', namespaces=NS),
            'expires': expires,
            'areas': [{
                'name': area.findtext('c:areaDesc', namespaces=NS),
                'polygons': [simplify(p.text) for p in area.findall('c:polygon', NS) if p.text],
            } for area in info.findall('c:area', NS)],
        })
    out.sort(key=lambda w: w['onset'] or '')
    return {'updated': now.isoformat(timespec='seconds'), 'warnings': out}


def main():
    if len(sys.argv) > 2:
        data = open(sys.argv[2], 'rb').read()
    else:
        req = urllib.request.Request(FEED, headers={'User-Agent': 'reijar.github.io/saa warnings'})
        data = urllib.request.urlopen(req, timeout=30).read()
    result = parse(data)
    with open(sys.argv[1], 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, separators=(',', ':'))
    print(f"{len(result['warnings'])} warnings")


if __name__ == '__main__':
    main()
