from pathlib import Path 
import json
import sys 

def load_crust_bench_benchmarks(r_path: Path):
    sys.path.append('/nas/CRUST-bench-repair/src')
    from benchmark import Benchmark
    C_BENCH = Path("/nas/CRUST-bench-repair/datasets/CBench")
    benchmarks = []
    for project in r_path.iterdir():
        if project.is_dir() and Path(project / "Cargo.toml").exists():
            project_name = project.name
            if Path(C_BENCH / project_name).exists():
                benchmarks.append(Benchmark(C_BENCH / project_name, project))
            else:
                c_proj = project_name
                if "proj_" in c_proj:
                    c_proj = c_proj.replace("proj_", "")
                    assert c_proj != ""
                if Path(C_BENCH / c_proj).exists():

                    benchmarks.append(Benchmark(C_BENCH / c_proj, project))
                else:
                    c_proj = c_proj.replace("_", "-")
                    benchmarks.append(Benchmark(C_BENCH / c_proj, project))
    return benchmarks

def generate_data_crust_bench(r_path, rri_type, rri_prompt_path, output_path): 
    
    benchmarks = load_crust_bench_benchmarks(r_path)
    for benchmark in benchmarks:
        j_object = {}
        j_object['name'] = benchmark.project_name
        for file in benchmark.c_files:
            
            j_object[file['file_name']] = file['content']
        j_object[rri_type] = ''
        rri_path = benchmark.rust_path / 'metadata' / 'invariants' / (rri_type+'.txt')
        with open(rri_path, "r", encoding='utf-8') as f:
            j_object[rri_type+"_pre_post_conditions"] = f.read()
        j_object['rri_prompt'] = ''
        if rri_prompt_path == '':
            rri_prompt_file = benchmark.rust_path / 'metadata' / 'invariants' / (rri_type+'_prompt.txt')
        else:
            rri_prompt_file = rri_prompt_path / (benchmark.project_name + '.prompt')
        with open(rri_prompt_file, "r", encoding='utf-8') as f:
            j_object['rri_prompt'] = f.read()
        output_file = output_path / f"{benchmark.project_name}.json"
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(j_object, f, indent=4)
        


def generate_data_compare_repair_revamp(with_rri_path, without_rri_path, rri_path, output_path):
    sys.path.append('/nas/long_context_reasoning/revamp/src/reasoning')
    from benchmark import load_benchmark as load_revamp_benchmark
    for path in with_rri_path.iterdir():
        j_object = {}
        if path.is_dir():
            project_name = path.name
            without_rri_project_path = without_rri_path / project_name
            rri_project_path = rri_path / project_name
            if without_rri_project_path.exists() and without_rri_project_path.is_dir():
                with_rri_benchmark = load_revamp_benchmark(str(path), Path('./'))
                without_rri_benchmark = load_revamp_benchmark(str(without_rri_project_path), Path('./'))
                rri_benchmark = load_revamp_benchmark(str(rri_project_path), Path('./'))
                j_object['name'] = project_name
                new_impl_with_rri = Path(with_rri_benchmark.new_adt_files[0]).read_text()
                new_impl_without_rri = Path(without_rri_benchmark.new_adt_files[0]).read_text()
                j_object['with_rri'] = new_impl_with_rri
                j_object['without_rri'] = new_impl_without_rri
                j_object['rri'] = rri_benchmark.rri
                j_object['comments'] = ''
                reasoning_path = Path(with_rri_benchmark.benchmark_path) / 'reasoning.txt'
                j_object['reasoning with rri'] = reasoning_path.read_text() if reasoning_path.exists() else ''
                reasoning_path = Path(without_rri_benchmark.benchmark_path) / 'reasoning.txt'
                j_object['reasoning without rri'] = reasoning_path.read_text() if reasoning_path.exists() else ''
                output_file = output_path / f"{project_name}.json"
                if output_file.exists():
                    with open(output_file, "r", encoding='utf-8') as f:
                        existing_data = json.load(f)
                    j_object['comments'] = existing_data.get('comments', '')
                with open(output_file, "w", encoding='utf-8') as f:
                    json.dump(j_object, f, indent=4)
                print(f"Written comparison for project {project_name} to {output_file}")


                
if __name__ == "__main__":
    path = Path('/nas/CRUST-bench-repair/datasets/inv_rust_path')
    # with_rri_path = path / 'with_rri'
    # without_rri_path = path / 'without_rri'
    # rri_path = Path('/nas/long_context_reasoning/revamp/revamp_scaled_gpt5_improved_all')
    output_path = Path('/nas/json_viewer_website/data/CRUST-bench/pre_post_conditions_c_source')
    output_path.mkdir(parents=True, exist_ok=True)
    generate_data_crust_bench(path, 'c', '', output_path)
    
    # generate_data_compare_repair_revamp(with_rri_path, without_rri_path, rri_path, output_path)
