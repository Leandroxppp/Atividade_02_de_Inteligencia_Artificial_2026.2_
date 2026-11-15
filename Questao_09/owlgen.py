"""Mini-gerador de OWL 2 (RDF/XML) — sem dependências externas."""
XSD = "http://www.w3.org/2001/XMLSchema#"
def _r(x): return f'rdf:resource="#{x}"'
def _members(names): return "".join(f'<rdf:Description rdf:about="#{n}"/>' for n in names)

def restr(kind, prop, val=None, datatype=None, n=None):
    if kind == "has":      return f'<owl:Restriction><owl:onProperty {_r(prop)}/><owl:hasValue {_r(val)}/></owl:Restriction>'
    if kind == "some":     return f'<owl:Restriction><owl:onProperty {_r(prop)}/><owl:someValuesFrom {_r(val)}/></owl:Restriction>'
    if kind == "dmax":     return (f'<owl:Restriction><owl:onProperty {_r(prop)}/><owl:someValuesFrom><rdfs:Datatype><owl:onDatatype rdf:resource="{XSD}{datatype}"/>'
                                   f'<owl:withRestrictions rdf:parseType="Collection"><rdf:Description><xsd:maxInclusive rdf:datatype="{XSD}{datatype}">{val}</xsd:maxInclusive></rdf:Description></owl:withRestrictions></rdfs:Datatype></owl:someValuesFrom></owl:Restriction>')
    if kind == "dmin":     return restr("dmax", prop, val, datatype).replace("maxInclusive", "minInclusive")
    raise ValueError(kind)

def inter(parts):  # parts: nomes de classe (str) ou XML de restrição
    items = "".join(_members([p]) if not p.startswith("<") else p for p in parts)
    return f'<owl:Class><owl:intersectionOf rdf:parseType="Collection">{items}</owl:intersectionOf></owl:Class>'

def build(base, classes, objprops, dataprops, individuals, disjoint=(), alldifferent=True):
    """classes: {nome: dict(sub=[...], equiv=[partes]|None, comment=str)}
       objprops: {nome: dict(dom, ran, inv=None, trans=False, func=False)}
       dataprops: {nome: dict(dom, ran, func=True)}
       individuals: {nome: dict(types=[...], obj={prop:[vals]}, data={prop:(valor, tipo)})}"""
    o = [f'<?xml version="1.0"?>\n<rdf:RDF xmlns="{base}#" xml:base="{base}" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
         f'xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:xsd="http://www.w3.org/2001/XMLSchema#">',
         f'<owl:Ontology rdf:about="{base}"/>']
    for n, c in classes.items():
        s = f'<owl:Class rdf:about="#{n}">'
        s += "".join(f'<rdfs:subClassOf {_r(p)}/>' for p in c.get("sub", []))
        if c.get("equiv"): s += f'<owl:equivalentClass>{inter(c["equiv"])}</owl:equivalentClass>'
        if c.get("comment"): s += f'<rdfs:comment>{c["comment"]}</rdfs:comment>'
        o.append(s + '</owl:Class>')
    for grp in disjoint:
        o.append(f'<owl:AllDisjointClasses><owl:members rdf:parseType="Collection">{_members(grp)}</owl:members></owl:AllDisjointClasses>')
    for n, p in objprops.items():
        s = f'<owl:ObjectProperty rdf:about="#{n}">'
        if p.get("trans"): s += '<rdf:type rdf:resource="http://www.w3.org/2002/07/owl#TransitiveProperty"/>'
        if p.get("func"):  s += '<rdf:type rdf:resource="http://www.w3.org/2002/07/owl#FunctionalProperty"/>'
        if p.get("dom"): s += f'<rdfs:domain {_r(p["dom"])}/>'
        if p.get("ran"): s += f'<rdfs:range {_r(p["ran"])}/>'
        if p.get("inv"): s += f'<owl:inverseOf {_r(p["inv"])}/>'
        o.append(s + '</owl:ObjectProperty>')
    for n, p in dataprops.items():
        s = f'<owl:DatatypeProperty rdf:about="#{n}">'
        if p.get("func", True): s += '<rdf:type rdf:resource="http://www.w3.org/2002/07/owl#FunctionalProperty"/>'
        s += f'<rdfs:domain {_r(p["dom"])}/><rdfs:range rdf:resource="{XSD}{p["ran"]}"/>'
        o.append(s + '</owl:DatatypeProperty>')
    for n, i in individuals.items():
        s = f'<owl:NamedIndividual rdf:about="#{n}">' + "".join(f'<rdf:type {_r(t)}/>' for t in i.get("types", []))
        for pr, vs in i.get("obj", {}).items(): s += "".join(f'<{pr} {_r(v)}/>' for v in vs)
        for pr, (v, t) in i.get("data", {}).items(): s += f'<{pr} rdf:datatype="{XSD}{t}">{v}</{pr}>'
        o.append(s + '</owl:NamedIndividual>')
    if alldifferent:   # Unique Name Assumption não vale em OWL: declaramos explicitamente que os indivíduos são distintos
        o.append('<owl:AllDifferent><owl:distinctMembers rdf:parseType="Collection">' + _members(list(individuals)) + '</owl:distinctMembers></owl:AllDifferent>')
    o.append('</rdf:RDF>')
    return "\n".join(o)
