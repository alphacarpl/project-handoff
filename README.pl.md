# Project Handoff Skill - instrukcja po polsku

Ta instrukcja jest napisana prostym jezykiem. Zakladam, ze nie musisz wiedziec, czym sa hooki Gita ani jak dziala `desktop.ini`.

## Co to jest?

Project Handoff to maly automat do projektow Git.

Po commicie albo na zyczenie tworzy i odswieza trzy rzeczy:

- `desktop.ini` - opis folderu widoczny dla Windows Explorera.
- `wiki/README.md` - prosty szablon dokumentacji projektu.
- `hours/sesje_i_czas.md` - szacunkowy czas pracy policzony z historii commitow.

Moze tez zainstalowac hook, czyli automatyczne polecenie, ktore uruchamia sie po kazdym `git commit`.

## Najprostsze wyjasnienie

Wyobraz sobie, ze kazdy projekt ma miec mala teczke przekazania:

- co to jest za projekt,
- kiedy byl ostatni commit,
- gdzie opisac cel projektu,
- ile mniej wiecej czasu bylo nad nim pracowane.

Ten skill pilnuje tej teczki za Ciebie.

## Co powstaje w projekcie?

Po uruchomieniu w projekcie pojawia sie:

```text
desktop.ini
wiki/
  README.md
hours/
  sesje_i_czas.md
```

Plik `wiki/README.md` jest tworzony tylko wtedy, gdy go jeszcze nie ma. Jesli juz istnieje, automat go nie nadpisuje.

## Wymagania

Potrzebujesz:

- Windows, macOS albo Linux.
- Python 3.
- Git.
- Projekt, ktory jest repozytorium Git.

Na Windowsie polecenia najlepiej uruchamiac w PowerShellu.

## Gdzie jest skill?

U Ciebie lokalnie skill jest tutaj:

```powershell
C:\Users\Wiktor\.codex\skills\project-handoff
```

Najwazniejszy skrypt jest tutaj:

```powershell
C:\Users\Wiktor\.codex\skills\project-handoff\scripts\project_manager.py
```

## Jednorazowe odswiezenie projektu

Uzyj tego, kiedy chcesz po prostu utworzyc albo odswiezyc pliki handoff.

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\project_manager.py" --project "C:\Sciezka\Do\Projektu" --description "Opis projektu"
```

Przyklad:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\project_manager.py" --project "C:\Users\Wiktor\Projects\crm" --description "CRM dla sprzedazy"
```

`--project` to sciezka do projektu.

`--description` to krotki opis projektu. Do `desktop.ini` trafia maksymalnie 28 znakow.

## Tryb handoff

Tryb handoff robi dwie rzeczy:

1. Odswieza pliki handoff.
2. Tworzy commit tylko z tymi plikami.

Polecenie:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\project_manager.py" --project "C:\Sciezka\Do\Projektu" --description "Opis projektu" --handoff
```

Domyslny komunikat commita to:

```text
chore: update project handoff
```

Mozesz ustawic wlasny:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\project_manager.py" --project "C:\Sciezka\Do\Projektu" --description "Opis projektu" --handoff --handoff-message "docs: odswiez handoff"
```

## Instalacja w jednym istniejacym projekcie

Jesli masz jeden konkretny projekt i chcesz, zeby handoff odswiezal sie po kazdym commicie:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\project_manager.py" --project "C:\Sciezka\Do\Projektu" --description "Opis projektu" --install-post-commit-hook
```

Od tej chwili po kazdym `git commit` Git uruchomi automat.

## Co jesli projekt ma juz hook?

Hook to plik:

```text
.git/hooks/post-commit
```

Jesli taki plik juz istnieje, skrypt go nie nadpisze. To celowe, bo w projekcie moze juz byc wazna automatyzacja.

Jesli mimo wszystko chcesz nadpisac istniejacy hook:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\project_manager.py" --project "C:\Sciezka\Do\Projektu" --description "Opis projektu" --install-post-commit-hook --force-hook
```

Uzywaj `--force-hook` ostroznie.

## Instalacja dla kazdego nowego projektu

To juz jest u Ciebie ustawione, ale polecenie wyglada tak:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\install_git_template.py"
```

To ustawia globalny szablon Gita. Kazde nowe repo utworzone przez `git init` dostanie hook automatycznie.

Wazne: to dziala tylko dla nowych repozytoriow, czyli takich, ktore dopiero utworzysz.

## Instalacja dla wielu istniejacych projektow

Do tego sluzy:

```powershell
C:\Users\Wiktor\.codex\skills\project-handoff\scripts\install_existing_repos.py
```

Najpierw zrob podglad. To niczego nie zmienia:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\install_existing_repos.py" --root "C:\Users\Wiktor\Projects" --dry-run
```

Skrypt wyszuka repozytoria Git pod folderem:

```text
C:\Users\Wiktor\Projects
```

i pokaze, gdzie zainstalowalby hook.

Jesli raport wyglada dobrze, uruchom bez `--dry-run`:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\install_existing_repos.py" --root "C:\Users\Wiktor\Projects"
```

Domyslnie skrypt nie nadpisuje istniejacych hookow.

Jesli chcesz nadpisac istniejace hooki:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\install_existing_repos.py" --root "C:\Users\Wiktor\Projects" --force
```

Najpierw prawie zawsze uzyj `--dry-run`.

## Jak ustawic opis projektu?

Najlepszy sposob to dodac w projekcie plik:

```text
.project-handoff-description
```

W pierwszej linii wpisz opis:

```text
CRM dla sprzedazy
```

Hook uzyje tego opisu. Jesli pliku nie ma, uzyje nazwy folderu projektu.

## Jak czytac raport batch installera?

Po uruchomieniu `install_existing_repos.py` zobaczysz raport.

Przyklady statusow:

```text
[installed] C:\Users\Wiktor\Projects\crm
[skipped] C:\Users\Wiktor\Projects\api - post-commit already exists
[dry-run] C:\Users\Wiktor\Projects\site - would install: ...
[failed] C:\Users\Wiktor\Projects\broken - ...
```

Znaczenie:

- `installed` - hook zostal zainstalowany.
- `skipped` - repo pominieto, zwykle dlatego, ze ma juz hook.
- `dry-run` - to tylko podglad, nic nie zmieniono.
- `failed` - cos poszlo nie tak.

## Czy to liczy prawdziwy czas pracy?

Nie w 100 procentach.

Git zapisuje czas commitow, ale nie wie, kiedy faktycznie pracowales. Skrypt patrzy na odstepy miedzy commitami.

Jesli dwa commity sa blisko siebie, skrypt uznaje, ze to jedna sesja pracy. Jesli przerwa jest dluga, zaczyna nowa sesje.

Domyslnie dluga przerwa to ponad 2 godziny.

Mozesz to zmienic:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\project_manager.py" --project "C:\Sciezka\Do\Projektu" --description "Opis projektu" --gap-minutes 90
```

## Najbezpieczniejszy sposob uzycia

Jesli chcesz objac wszystkie swoje stare projekty:

1. Wybierz folder, gdzie trzymasz projekty, np. `C:\Users\Wiktor\Projects`.
2. Uruchom `--dry-run`.
3. Przeczytaj raport.
4. Uruchom instalacje bez `--dry-run`.
5. Nie uzywaj `--force`, chyba ze wiesz, ze chcesz nadpisac hooki.

Polecenia:

```powershell
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\install_existing_repos.py" --root "C:\Users\Wiktor\Projects" --dry-run
python "C:\Users\Wiktor\.codex\skills\project-handoff\scripts\install_existing_repos.py" --root "C:\Users\Wiktor\Projects"
```

## Jak to wylaczyc w jednym projekcie?

Usun plik:

```text
.git/hooks/post-commit
```

Tylko upewnij sie, ze nie byl to hook potrzebny do czegos innego.

## Jak to wylaczyc dla nowych projektow?

Usun globalne ustawienie:

```powershell
git config --global --unset init.templateDir
```

To nie usuwa hookow z juz istniejacych projektow. Wylacza tylko automatyczne dodawanie hooka do nowych repo po `git init`.
