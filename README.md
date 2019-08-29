# h2pdf

Download and export galleries on E-Hentai/ExHentai in PDF format.

## Usage

`h2pdf.py [-h] [-i MEMBER_ID] [-p PASS_HASH] [-e] [-r] [-s {e-hentai,exhentai}] <gallery>`

- `-i` Your member ID from the cookie named `ipb_member_id`.
- `-p` Your password hash from the cookie named `ipb_pass_hash`.
- `-e` Also export images to the `images` directory.
- `-r` Download original images if available (valid account required).
- `-s` Source to download from. `e-hentai` (default) or `exhentai` (valid account required).
- `gallery` Full URL or gallery ID & token (e.g. `1425378/b6b405e7eb`).

The PDF files should be saved in the `galleries` directory.

## Warning

If you try too hard, your IP address may be banned for 24 hours.

## TODO

- [x] Error alerts & retries.
- [x] Support for multithreading.
- [ ] Support for saving multiple galleries at one time.
- [ ] Support for proxy.
- [ ] Progress bar.