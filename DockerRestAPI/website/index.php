<html>
    <head>
        <title>CIS 322 REST-api demo: Laptop list</title>
    </head>

    <body>
        <h1>List of laptops</h1>
		<?php
		$allowed = ["listAll", "listOpenOnly", "listCloseOnly"];
		$list = $_GET["list"] ?? "listAll";
		if (!in_array($list, $allowed)) { $list = "listAll"; }

		$top = $_GET["top"] ?? "";
		$url = "http://laptop-service/" . $list;
		if ($top !== "") {
			$url .= "?top=" . urlencode($top);
		}

		$json = @file_get_contents($url);
		?>
		<?php if ($json === false): ?>
			<p>Could not get times. Check that "top" is a whole number of 1 or more.</p>
		<?php else: ?>
			<ul>
			<?php
			$rows = json_decode($json);
			foreach ($rows as $row) {
				$parts = [];
				if (isset($row->open)) { $parts[] = "Open: " . $row->open; }
				if (isset($row->close)) { $parts[] = "Close: " . $row->close; }
				echo "<li>" . implode(" | ", $parts) . "</li>";
			}
			?>
			</ul>
		<?php endif; ?>
		<form method="get">
			<select name="list">
				<option value="listAll">All times</option>
				<option value="listOpenOnly">Open times only</option>
				<option value="listCloseOnly">Close times only</option>
			</select>
			<input type="number" name="top" min="1" placeholder="top k (optional)">
			<button type="submit">Show</button>
		</form>
    </body>
</html>
