from csv import DictReader, DictWriter
from pathlib import Path
from typing import Dict, Iterable, List, NamedTuple, Optional, FrozenSet

from bs4 import BeautifulSoup
from bs4.element import Tag


class Spell(NamedTuple):
    name: str
    url: str
    level: int
    summary: str
    source: str
    traditions: FrozenSet[str]
    rarity: str
    traits: FrozenSet[str]
    is_cantrip: bool
    is_focus: bool
    is_heightenable: bool

    def __repr__(self):
        return f"Spell(name='{self.name}', level={self.level}, summary='{self.summary}')"


def data_dir() -> Path:
    return Path(__file__).parent / "data"


def iter_csv() -> Iterable[Dict[str, str]]:
    source_file = data_dir() / "RadGridExport.csv"
    with source_file.open() as file:
        reader = DictReader(file)
        for row in reader:
            yield row


def html_get_text(html_fragment: str) -> str:
    return BeautifulSoup(html_fragment, "html.parser").get_text()


def handle_row(row: Dict[str, str]) -> Spell:
    anchor = BeautifulSoup(row["Name"], "html.parser").find("a")
    url_path = anchor.attrs.get("href") if anchor and isinstance(anchor, Tag) else ""
    return Spell(
        name=html_get_text(row["Name"]),
        url=f"https://2e.aonprd.com/{url_path}",
        level=int(html_get_text(row["Level"])),
        summary=row["Summary"],
        source=html_get_text(row["Source"]),
        traditions=frozenset(html_get_text(row["Traditions"]).split(", ")),
        rarity=html_get_text(row["Rarity"]),
        traits=frozenset(html_get_text(row["Traits"]).split(", ")),
        is_cantrip=html_get_text(row["Cantrip"]).lower() == "true",
        is_focus=html_get_text(row["Focus"]).lower() == "true",
        is_heightenable=html_get_text(row["Heightenable"]).lower() == "true",
    )


def write_csv(
    output: Path, spells: Iterable[Spell], max_level: Optional[int] = None, traditions: Optional[List[str]] = None
):
    traditions_set = set(traditions) if traditions else None

    def include_spell(spell_to_check: Spell) -> bool:
        if max_level and spell_to_check.level > max_level:
            return False
        if traditions_set and not traditions_set & spell_to_check.traditions:
            return False
        return True

    with output.open("w") as file:
        writer = DictWriter(
            file,
            fieldnames=(
                "Name",
                "Level",
                "Description",
                "Rare or Uncommon",
                "Is Cantrip",
                "Is Focus",
                "Heightenable",
                "Traditions",
                "URL",
            ),
        )
        writer.writeheader()
        for spell in spells:
            if include_spell(spell):
                writer.writerow(
                    {
                        "Name": spell.name,
                        "Level": str(spell.level),
                        "Description": spell.summary,
                        "Rare or Uncommon": spell.rarity if spell.rarity != "Common" else "",
                        "Is Cantrip": "✓" if spell.is_cantrip else "",
                        "Is Focus": "✓" if spell.is_focus else "",
                        "Heightenable": "✓" if spell.is_heightenable else "",
                        "Traditions": ", ".join(sorted(spell.traditions)),
                        "URL": spell.url,
                    }
                )


def main():
    spells = map(handle_row, iter_csv())
    csv_path = data_dir() / "spells.csv"
    write_csv(csv_path, spells)
    print(f"Spells CSV written to {csv_path}. ✨ 🍰 ✨")


if __name__ == "__main__":
    main()
