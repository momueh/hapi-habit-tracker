import typer

app = typer.Typer()


@app.command()
def hello():
    typer.echo("Hello from the Habit Tracker!")


if __name__ == "__main__":
    app()
