# TODO

## Completed

- [x] Install Home Assistant test dependencies
- [x] Run the full local test suite
- [x] Fix failing tests
- [x] Reach at least 90% coverage
- [x] Generate coverage reports
  - [x] XML report: `coverage.xml`
  - [x] HTML report: `htmlcov/index.html`
- [x] Add a local manual Home Assistant launcher for the real TCP device

## Next

- [x] Report the latest test and coverage results
- [x] Run `hassfest` validation
- [x] Add `hassfest` to GitHub Actions CI

## Future ideas

- [ ] Implement Modbus RTU / serial transport
- [ ] Add protocol selection in the config flow for TCP vs Serial
- [ ] Add serial transport settings in the options flow
- [ ] Refine enum and status-word decoding
- [ ] Expand diagnostics with more interpreted device details
- [ ] Improve transport abstraction for TCP and RTU backends
- [ ] Review entity metadata against Home Assistant long-term statistics rules
- [ ] Revisit daily resettable energy semantics after more runtime validation
- [ ] Consider follow-up skills deliverables for Home Assistant, HACS, and device Modbus handling
