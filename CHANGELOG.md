# Changelog

Notable changes per release. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Every entry ends with the issue or pull request it came from, written bare —
`(#133)`, not a markdown link — so the paragraph saying *what* changed stays one
click from the discussion saying *why*. Issue numbers refer to
[L0laapk3/FactorioMaps](https://github.com/L0laapk3/FactorioMaps/issues).

`updates.json` stays as it is: the game reads it to show the update notice, and
it wants one line per change, not prose.

## [5.0.1] — 2026-08-11

### Changed

- **The info button moved to the bottom right corner, and the attribution bar is gone.** The strip reading "Leaflet | FactorioMaps" sat in that corner doing nothing a reader wanted; the credits it carried were already in the info panel, which names and links FactorioMaps, Leaflet, mozjpeg and Factorio, and now links this fork beside the line describing what it changed. (#6)

### Fixed

- **Downloading a Factorio client no longer fails at the last step.** The
  entrypoint seeded `config.ini` into a `config/` directory it had not created,
  which under `set -euo pipefail` killed the container — after the client and
  the expansion had already been fetched, so a gigabyte and a half of download
  was discarded each time. A render generally escaped it, because the caller
  usually mounts a staging directory that already has `config/` in it.

- **A render that was killed no longer breaks every render after it.** `ref.py` indexes what the
  previous snapshot holds by listing its directories and renaming `.png` to `.jpg`, which assumes
  every name in there has a compressed tile beside it. A snapshot whose run was killed between
  `zoom.py` writing a png and compressing it does not — so each leftover became an index entry
  pointing at a jpg nothing ever wrote, and the comparison it scheduled raised `FileNotFoundError`
  out of the worker pool, losing that surface's whole cross-referencing pass. Reported from a
  sixteen-surface Space Age map that printed pages of these on every run. (#4)

- **The full screen button appears on the map again.** `leaflet.fullscreen` puts its button inside the zoom control's container unless `forceSeparateButton` says otherwise, and the viewer moves the zoom control to the other corner on the following line — which rebuilds that container and drops the button with it. Nobody had a full screen button since the control was first added, on either the old plugin or the new one. (#6)

## [5.0.0] — 2026-08-11

### Added

- **Space Age maps.** `--all-surfaces` captures every surface a force has
  charted — each visited planet and each space platform — in one run instead of
  one invocation per surface. The viewer grew a browser for them: planets down
  the left, platforms down the right under the name the player gave them and the
  planet they are parked at, rich text in those names rendered as the icons it
  stands for. Verified against a five snapshot timeline that grows from 7
  surfaces to 20 across Nauvis, Vulcanus, Fulgora, Gleba and 16 platforms.

- **An info panel.** The button in the bottom left opens what the map cannot
  say for itself: how many snapshots and surfaces it holds, the Factorio
  version, who played and for how long, every mod and its version, and credits.

- **Link previews.** Opengraph and Twitter card tags are filled in per map, so a
  shared link shows the Nauvis thumbnail and the snapshot, surface and mod
  counts rather than a bare URL.

- **A container for running captures on a server.** Factorio only renders in the
  full client, so headless has never worked and the README said so. `docker/`
  runs the real client against a virtual display; because Xvfb has no direct
  rendering and plain GLX therefore lands on llvmpipe, VirtualGL renders through
  the GPU instead, worth about 30% wall clock on an Intel UHD 620. Software
  rendering stays a supported fallback — slower, not broken.

- **Space Age maps.** `--all-surfaces` captures every surface a force has
  charted — each visited planet and each space platform — in one run instead of
  one invocation per surface. The viewer grew a browser for them: planets down
  the left, platforms down the right under the name the player gave them and the
  planet they are parked at, rich text in those names rendered as the icons it
  stands for. (#133)

- **An info panel.** The button in the bottom left opens what the map cannot say
  for itself: how many snapshots and surfaces it holds, the Factorio version, who
  played and for how long, every mod and its version, and credits.

- **Link previews.** Opengraph and Twitter card tags are filled in per map, so a
  shared link shows the Nauvis thumbnail and the snapshot, surface and mod counts
  rather than a bare URL.

- **A container for running captures on a server.** Factorio only renders in the
  full client, so headless has never worked. `docker/` runs the real client
  against a virtual display; because Xvfb has no direct rendering and plain GLX
  therefore lands on llvmpipe, VirtualGL renders through the GPU instead, worth
  about 30% wall clock on an Intel UHD 620. Software rendering stays a supported
  fallback — slower, not broken.

### Fixed

- **Captures no longer stop after the first surface.** The surface loop declared
  itself done once one surface finished, so the game sat on its "finished
  capturing" screen while the script waited for a `done.txt` that would never be
  written — a hang with no error, on any map with more than one surface. Every
  requested surface is now captured in a single launch. (#116)

- **A fresh install can compress images again.** `PyTurboJPEG>=1.1.5` has no
  upper bound, and 2.0 dropped support for libjpeg-turbo 2.x — which is exactly
  what `mozjpeg/` ships. Every new install therefore died on import with a
  message about a library version, nowhere near the requirement that chose it.
  Pinned below 2.0.

- **The web assets are readable by whoever runs the map.** `updateLib` copies
  them out of a `TemporaryDirectory`, which exists at mode 0700, and `copytree`
  carried that straight into `web/lib` — so a map generated by one user and
  served by another had no stylesheets.

- **Item icons in map labels resolve for virtual signals.** Rich text writes
  `[virtual-signal=x]`, the data stage indexes those prototypes as `virtual`,
  and nothing reconciled the two, so the label fell back to raw text. (#93)

- **A missing `mod-list.json` or `player-data.json` no longer ends the run.**
  Factorio writes both on first launch; a mod folder that had never seen one
  crashed the script instead of being given one.

- **`--dry` keeps the icons it did not generate.** A dry run never receives icon
  paths from the game, and rebuilt the label folder from that emptiness —
  deleting the icons a real run had extracted.

- **Only the factorio this script started gets killed.** It ran `killall
  factorio`, which on a machine playing the game meant the capture ended the
  player's session too. (#102)

- **A mod may un-hide a surface again.** `surface_set_hidden(surface, false)`
  called a method that does not exist on a Lua table.

- **Progress is legible in a log.** The crop, ref and zoom steps redrew a bar
  with carriage returns, which a redirected log or `docker logs` renders as one
  ever-growing line. They now print a line every few percent when output is not
  a terminal, and are unchanged when it is.

- **Captures no longer stop after the first surface.** The surface loop declared
  itself done once one surface finished, so the game sat on its "finished
  capturing" screen while the script waited for a `done.txt` that would never be
  written — a hang with no error, on any map with more than one surface. (#116)

- **A fresh install can compress images again.** `PyTurboJPEG>=1.1.5` has no
  upper bound, and 2.0 dropped support for libjpeg-turbo 2.x — which is exactly
  what `mozjpeg/` ships. Every new install therefore died on import with a
  message about a library version, nowhere near the requirement that chose it.

- **The web assets are readable by whoever runs the map.** `updateLib` copies
  them out of a `TemporaryDirectory`, which exists at mode 0700, and `copytree`
  carried that straight into `web/lib`.

- **Item icons in map labels resolve for virtual signals.** Rich text writes
  `[virtual-signal=x]`, the data stage indexes those prototypes as `virtual`, and
  nothing reconciled the two. (#93)

- **A missing `mod-list.json` or `player-data.json` no longer ends the run.**
  Factorio writes both on first launch; a mod folder that had never seen one
  crashed the script instead of being given one.

- **`--dry` keeps the icons it did not generate.** A dry run never receives icon
  paths from the game, and rebuilt the label folder from that emptiness.

- **Only the factorio this script started gets killed.** It ran `killall
  factorio`, which on a machine playing the game ended the player's session too.
  (#102)

- **A mod may un-hide a surface again.** `surface_set_hidden(surface, false)`
  called a method that does not exist on a Lua table.

- **Progress is legible in a log.** The crop, ref and zoom steps redrew a bar
  with carriage returns, which a redirected log or `docker logs` renders as one
  ever-growing line.

### Changed

- **The mod targets Factorio 2.1 and needs it.** `info.json` declares
  `factorio_version: 2.1`; 1.1 users stay on 4.4.0. The 2.0 API moves this
  required — `helpers.write_file`, `prototypes.*`, `script.active_mods`, the
  loss of the `flying-text` entity, `player` becoming `character` in filters,
  chart tag types defaulting to nil — are the bulk of the port, along with
  hiding the new cloud and fog layers so they do not settle over the map. (#133)

- **macOS is a supported platform.** The binary is found in both standalone and
  Steam locations, the user data folder is located per platform, `libturbojpeg`
  is taken from the system when the bundled one does not fit the architecture,
  and tag icons are read from inside the application bundle.

[5.0.0]: https://github.com/lordfiSh/FactorioMaps/releases/tag/v5.0.0

- **The mod targets Factorio 2.1 and needs it.** `info.json` declares
  `factorio_version: 2.1`; 1.1 users stay on 4.4.0. (#133)

- **macOS is a supported platform.** The binary is found in both standalone and
  Steam locations, the user data folder is located per platform, `libturbojpeg`
  is taken from the system when the bundled one does not fit the architecture,
  and tag icons are read from inside the application bundle.
