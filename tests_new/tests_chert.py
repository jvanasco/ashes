"""
this is a manual test

the chert templates were copied from https://github.com/mahmoud/chert
the json was generated by hacking chert and pretty-dumping the render context
"""
import os
import codecs
import json
import ashes
from tests_compiled_loaders import TemplatesLoader, TemplatesLoaderLazy


_chert_dir = '../tests/templates_chert'

_chert_files_all = os.listdir(_chert_dir)
_chert_files_html = [i for i in _chert_files_all if i[-5:] == '.html']
_chert_files_html_json = [i for i in _chert_files_all if i[-10:] == '.html.json']

chert_data = {}
for f in _chert_files_html:
    f_json = f + '.json'
    if f_json in _chert_files_html_json:
        json_data = codecs.open(os.path.join(_chert_dir, f_json), 'r', 'utf-8').read()
        chert_data[f] = json.loads(json_data)

# okay, let's generate the expected data...
expected = {}
ashesEnv = ashes.AshesEnv(paths=[_chert_dir,], )
for (fname, fdata) in chert_data.items():
    rendered = ashesEnv.render(fname, fdata)
    expected[fname] = rendered
    
render_fails = {}

# now let's generate some cachable templates
ashesPreloader = TemplatesLoader(directory=_chert_dir)
cacheable_templates = ashesPreloader.generate_all_cacheable()

# make 2 extra versions for testing...
cacheable_templates_ast = {}
cacheable_templates_python_string = {}
for (k, payload) in cacheable_templates.items():
    cacheable_templates_ast[k] = {'ast': payload['ast'], }
    cacheable_templates_python_string[k] = {'python_string': payload['python_string'], }



# let's ensure this works...
rendered_pairing = {}
for pairing in (('cacheable_templates', cacheable_templates),
                ('cacheable_templates_ast', cacheable_templates_ast),
                ('cacheable_templates_python_string', cacheable_templates_python_string),
): 
    print "----"
    pairing_name = pairing[0]
    print "Testing %s" % pairing_name
    rendered_pairing[pairing_name] = {}
    pairing_stash = rendered_pairing[pairing_name]

    # build a new cacheable templates...
    ashesLoaderAlt = TemplatesLoader()
    ashesEnvAlt = ashes.AshesEnv(loaders=(ashesLoaderAlt, ))
    ashesLoaderAlt.load_from_cacheable(pairing[1])

    for (fname, fdata) in chert_data.items():
        rendered = ashesEnvAlt.render(fname, fdata)
        pairing_stash[fname] = rendered
        if rendered == expected[fname]:
            print "+", fname
        else:
            print "x", fname
            if pairing_name not in render_fails:
                render_fails[pairing_name] = {}
            render_fails[pairing_name][fname] = rendered

print "Fails?"
print render_fails


if False:
    import timeit

    def bench_chert():
        ashesEnv = ashes.AshesEnv(paths=[_chert_dir,], )
        for (fname, fdata) in chert_data.items():
            rendered = ashesEnv.render(fname, fdata)

    def bench_chert_cache():
        ashesLoaderAlt = TemplatesLoader()
        ashesEnvAlt = ashes.AshesEnv(loaders=(ashesLoaderAlt, ))
        ashesLoaderAlt.load_from_cacheable(cacheable_templates)
        for (fname, fdata) in chert_data.items():
            rendered = ashesEnv.render(fname, fdata)

    # 100 renders = 3.10
    print timeit.timeit('bench_chert()', 'from __main__ import bench_chert', number=100)
    # 100 renders = 0.90
    print timeit.timeit('bench_chert_cache()', 'from __main__ import bench_chert_cache', number=100)
    exit()

