# pinterest-pins

Public image hosting for Pinterest bulk-upload pins.

Finished pins are saved in `pins/` as `<PIN_ID>.png`. Pinterest's bulk-upload CSV points at each one through its direct link:

`https://raw.githubusercontent.com/Anusha-Skaties/pinterest-pins/main/pins/<PIN_ID>.png`

## Outfit pages

Each pin can link to its own "shop the look" page that lists every garment with its affiliate link:

`https://anusha-skaties.github.io/pinterest-pins/outfits/<PIN_ID>/`

To add one, write `outfits/<PIN_ID>/outfit.json` (format at the top of `tools/make_outfit_page.py`), then run:

```
python3 tools/make_outfit_page.py <PIN_ID>
```
