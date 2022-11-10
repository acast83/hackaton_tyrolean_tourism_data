from pathlib import Path
import click


def read_model_file(file: Path) -> list:
    def prep_class_line(_line: str):
        return _line[:_line.find('(')] + '{'

    def prep_field_line(_line: str):
        return _line[:_line.find('=')].rstrip()

    def prep_fk_field_line(_line: str):
        _line = _line[_line.find('(') + 2:]
        return _line[:_line.find("'")].split('.')[-1]
    
    def is_tortoise_model_file(file_lines: list) -> bool:
        for line in file_lines:
            if 'from tortoise' in line and 'fields' in line:
                return True
        return False
        

    result = list()
    count = -1

    with file.open() as f:
        file_list = f.readlines()
        
        if is_tortoise_model_file(file_list):
            for line_number, line in enumerate(file_list):

                if line.startswith('class '):
                    class_obj = {
                        'name': prep_class_line(line),
                        'fields': [],
                        'foreign_keys': [],
                    }
                    result.append(class_obj)
                    count += 1
                elif count >= 0 and 'fields' in line and line.strip() and line.strip()[0] != '#':
                    if 'ForeignKeyField' in line or 'OneToOneField' in line:
                        result[count]['foreign_keys'].append(prep_fk_field_line(line))
                    result[count]['fields'].append(prep_field_line(line))
        else:
            raise ValueError(f'"{file}" is not a valid tortoise model file.')

    result = [class_ for class_ in result if len(class_['fields']) > 1]
    for i in range(len(result)):
        result[i]['fields'].append('}\n')

    return result


def prepare_diagram(classes: list):
    result = list()
    result.append('```mermaid\nclassDiagram')

    # add links
    for class_ in classes:
        for fk in class_['foreign_keys']:
            link = f'{class_["name"][6:-1]}-->{fk}'
            result.append(link)
    else:
        result.append('')

    for class_ in classes:
        result.append(class_['name'])
        result += class_['fields']
    else:
        result.append('')

    result.append('```')
    return result


@click.command()
@click.option("--files", "-f", required=True, multiple=True)
def main(files):
    result = list()

    for file in files:
        if file[0] != '/':
            file = Path(Path.cwd(), file).resolve(strict=True)
        else:
            file = Path(file).resolve(strict=True)
        result += read_model_file(file)

    diagram_list = prepare_diagram(result)

    new_diagram = Path('models_diagram.md').resolve()
    with new_diagram.open('w') as f:
        f.write('\n'.join(diagram_list))
    print(f'New diagram saved as {new_diagram}')


if __name__ == "__main__":
    main()
