from pathlib import Path 
import json
import sys 
sys.path.append('/nas/long_context_reasoning/revamp/src/reasoning')
from benchmark import load_benchmark


def generate_data_compare_repair_revamp(with_rri_path, without_rri_path, rri_path, output_path):
    
    for path in with_rri_path.iterdir():
        j_object = {}
        if path.is_dir():
            project_name = path.name
            without_rri_project_path = without_rri_path / project_name
            rri_project_path = rri_path / project_name
            if without_rri_project_path.exists() and without_rri_project_path.is_dir():
                with_rri_benchmark = load_benchmark(str(path), Path('./'))
                without_rri_benchmark = load_benchmark(str(without_rri_project_path), Path('./'))
                rri_benchmark = load_benchmark(str(rri_project_path), Path('./'))
                j_object['name'] = project_name
                new_impl_with_rri = Path(with_rri_benchmark.new_adt_files[0]).read_text()
                new_impl_without_rri = Path(without_rri_benchmark.new_adt_files[0]).read_text()
                j_object['with_rri'] = new_impl_with_rri
                j_object['without_rri'] = new_impl_without_rri
                j_object['rri'] = rri_benchmark.rri
                j_object['comments'] = ''

                output_file = output_path / f"{project_name}.json"
                if output_file.exists():
                    with open(output_file, "r") as f:
                        existing_data = json.load(f)
                    j_object['comments'] = existing_data.get('comments', '')
                with open(output_file, "w") as f:
                    json.dump(j_object, f, indent=4)
                print(f"Written comparison for project {project_name} to {output_file}")


                
if __name__ == "__main__":
    path = Path('/nas/long_context_reasoning/revamp/results3/repair_ablations/o4-mini/analysis/with_rri_but_not_without')
    with_rri_path = path / 'with_rri'
    without_rri_path = path / 'without_rri'
    rri_path = Path('/nas/long_context_reasoning/revamp/revamp_scaled_gpt5_improved_all')
    output_path = Path('/nas/json_viewer_website/data/fails_with_rri_but_works_without_rri')
    output_path.mkdir(parents=True, exist_ok=True)
    generate_data_compare_repair_revamp(with_rri_path, without_rri_path, rri_path, output_path)