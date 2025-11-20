def chain_peers_search(base_symbol, from_date, to_date, successful, visited_symbols=None):
    if visited_symbols is None:
        visited_symbols = set()

    queue = deque()
    queue.append(base_symbol)

    while queue:
        curr_symbol = queue.popleft()

        if curr_symbol in visited_symbols:
            continue

        visited_symbols.add(curr_symbol)

        if insert_to_db(curr_symbol, from_date, to_date):
            successful.add(curr_symbol)
            print(f"[INFO] Successfully added {curr_symbol}")
            print(f"[INFO] Researched {len(successful)} stocks.")

            peers = get_peers(curr_symbol)
            for peer in peers:
                if peer not in visited_symbols:
                    queue.append(peer)
        else:
            print(f"[INFO] No news for {curr_symbol}")

    return successful, visited_symbols



def master_search(from_date, to_date, n, init_symbol=None):
    visited = set()
    successful = set()

    if init_symbol:
        successful, visited = chain_peers_search(init_symbol, from_date, to_date, successful, visited)
    else:
        random_init = random.choice(list(tech_master_symbol_set))
        successful, visited = chain_peers_search(random_init, from_date, to_date, successful, visited)

    i = 0
    while len(successful) < n:
        print(f"Iteration {i}")

        # Only use tech_master_symbol_set if peer chain has dried up
        next_candidates = tech_master_symbol_set - visited

        if not next_candidates:
            print("[INFO] Exhausted tech master list, trying to discover more through deeper peer chaining.")
            break  # or fall back to another source if you want

        next_symbol = random.choice(list(next_candidates))
        successful, visited = chain_peers_search(next_symbol, from_date, to_date, successful, visited)

        i += 1

    print(f"[INFO] Collected news for {len(successful)} unique symbols.")
    return successful