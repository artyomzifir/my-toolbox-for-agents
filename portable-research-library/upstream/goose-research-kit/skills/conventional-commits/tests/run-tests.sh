#!/bin/sh
# Checks for scripts/commit-msg. Run: sh tests/run-tests.sh
set -u
hook=$(dirname "$0")/../scripts/commit-msg
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
failed=0

check() { # label expected message
    printf '%s' "$3" > "$tmp/msg"
    if sh "$hook" "$tmp/msg" >/dev/null 2>&1; then got=ok; else got=fail; fi
    if [ "$got" = "$2" ]; then
        printf 'PASS  %-32s %s\n' "$1" "$got"
    else
        printf 'FAIL  %-32s got=%s want=%s\n' "$1" "$got" "$2"
        failed=$((failed + 1))
    fi
}

check 'feat, no scope'            ok   'feat: add parser for arrays'
check 'scope'                     ok   'feat(parser): add array support'
check 'breaking marker'           ok   'feat(api)!: drop v1 endpoints'
check 'breaking footer'           ok   'chore!: drop node 6

BREAKING CHANGE: node 6 is unsupported.'
check 'BREAKING-CHANGE synonym'   ok   'refactor!: drop node 6

BREAKING-CHANGE: node 6 is unsupported.'
check 'body and footers'          ok   'fix: prevent racing of requests

Add a request id to drop stale responses.

Reviewed-by: Z
Refs: #123'
check 'multi-paragraph body'      ok   'docs: explain retries

First paragraph.

Second paragraph.'
check 'revert'                    ok   'revert: feat(api): send welcome email

This reverts commit 1234abc.'
check 'missing type'              fail 'Added new parser'
check 'missing colon'             fail 'feat add parser'
check 'missing space'             fail 'feat:Add parser'
check 'trailing period'           fail 'feat: add parser.'
check 'uppercase description'     fail 'feat: Add parser'
check 'unknown type'              fail 'update: change stuff'
check 'header over 72 chars'      fail 'feat: add a very long description that certainly exceeds the seventy two character limit'
check 'no blank line before body' fail 'feat: add parser
body right after'
check 'lowercase breaking token'  fail 'fix: drop endpoints

breaking change: endpoints removed'
check 'footer token with space'   fail 'fix: prevent race

Reviewed by: Z'
check 'co-author trailer'          fail 'feat: add parser

Co-authored-by: goose <goose@example.com>'
check 'fixup marker'              fail 'fixup! feat: add parser'
check 'empty message'             fail ''

[ "$failed" -eq 0 ] || { echo "$failed check(s) failed"; exit 1; }
echo 'all checks passed'
