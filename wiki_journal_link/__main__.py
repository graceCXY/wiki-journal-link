import sys
import click

from pipeline import process_citation_to_scholars, process_citation_to_SIM, process_citation_to_either


@click.group()
@click.version_option("1.0.0")
def main():
    """A command line tool for process wikipedia citations for journal to a internet archive link in the SIM 
    collection or sholar.archive.org """
    pass


@main.command()
@click.argument('scholar', required=False)
def scholar(**kwargs):
    """Generate a scholar.archive.org link"""
    result = process_citation_to_scholars(kwargs.get("scholar"))
    click.echo(result)


@main.command()
@click.argument('sim', required = False)
def sim(**kwargs):
    """Generate link to a link in the SIM collection"""
    result = process_citation_to_SIM(kwargs.get("sim"))
    click.echo(result)


@main.command()
@click.argument('either', required = False)
def either(**kwargs):
    """Generate link to a link in the SIM collection"""
    result = process_citation_to_either(kwargs.get("either"))
    click.echo(result)



if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("Wikipedia Journal Linker - improve wikipedia article connectivity")
    main()