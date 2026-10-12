
        # Load file
        if not infile.Open('r'):
            DiagWrite("GridLoad file error\n")
            return

        filetext = infile.ReadLines()
        infile.Close()

        self.WriteVDU("Reading grid data...")

        storeversion = 0
        gridtags = list(self.gridtags)
        numlines = len(filetext)
        linecount = 0

        for readline in filetext:
            if not readline.strip(): break

            readdata = readline.split(maxsplit=3)
            if not readdata: continue

            if readdata[0] == "gsv":
                storeversion = int(readdata[1])

            elif readdata[0] == "num":
                continue

            elif readdata[0] == "g":
                sizes = readline.split()
                gridid = sizes[1]
                numrows = int(sizes[3])
                numcols = int(sizes[5])

                if storeversion == 1:
                    index = int(gridid)
                    while index >= len(gridtags):
                        newtag = f"Grid {len(gridtags)}"
                        self.AddGrid(newtag, wx.Size(20, 20))
                        gridtags.append(newtag)
                    gridtag = gridtags[index]
                else:
                    gridtag = gridid
                    if gridtag not in self.grids:
                        self.AddGrid(gridtag, wx.Size(numrows, numcols))

                grid = self.grids[gridtag]

                if numrows > grid.GetNumberRows():
                    grid.AppendRows(numrows - grid.GetNumberRows())
                if numcols > grid.GetNumberCols():
                    grid.AppendCols(numcols - grid.GetNumberCols())

                grid.ClearGrid()

            else:
                if len(readdata) < 4: continue

                gridid = readdata[0]
                row = int(readdata[1])
                col = int(readdata[2])
                celldata = readdata[3].strip()

                if storeversion == 1:
                    gridtag = gridtags[int(gridid)]
                else:
                    gridtag = gridid

                self.grids[gridtag].SetCellValue(row, col, celldata)

            linecount += 1
            if self.gauge and linecount % 2000 == 0:
                self.gauge.SetValue(int(100 * linecount / numlines))
                wx.YieldIfNeeded()

        self.WriteVDU("OK\n")
        if self.gauge: self.gauge.SetValue(0)

        # Read column sizes file
        filepath = gridpath + "/" + filetag + "-gridsize.txt"
        infile = TextFile(filepath)

        if not infile.Exists(): return
        if not infile.Open('r'):
            DiagWrite("GridLoad size file error\n")
            return

        filetext = infile.ReadLines()
        infile.Close()

        for readline in filetext:
            readdata = readline.split()
            if len(readdata) < 5: continue

            gridid = readdata[1]
            col = int(readdata[3])
            width = int(readdata[4])

            if storeversion == 1:
                gridtag = gridtags[int(gridid)]
            else:
                gridtag = gridid

            if gridtag in self.grids:
                self.grids[gridtag].SetColSize(col, width)
