Add-Type -AssemblyName System.Drawing
$base=(Get-Location).Path
$out=Join-Path $base 'results\lab01'
$routes=Import-Csv (Join-Path $out 'route_data.csv')
$metrics=Import-Csv (Join-Path $out 'metrics.csv')
$w=1200; $h=760
$bmp=[System.Drawing.Bitmap]::new($w,$h)
$g=[System.Drawing.Graphics]::FromImage($bmp); $g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias; $g.Clear([System.Drawing.Color]::White)
$font=[System.Drawing.Font]::new('Segoe UI',10); $small=[System.Drawing.Font]::new('Segoe UI',8); $title=[System.Drawing.Font]::new('Segoe UI',20,[System.Drawing.FontStyle]::Bold); $head=[System.Drawing.Font]::new('Segoe UI',11,[System.Drawing.FontStyle]::Bold)
$black=[System.Drawing.Brushes]::Black; $blue=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(35,110,210),3); $orange=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(235,125,35),3); $green=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(35,155,95),3)
$g.DrawString('Lab 1 - Route comparison: KUL to KEF',$title,$black,35,20)
$panelW=1100; $panelH=600; $x0=50; $y0=80
# Q1 comparison of BFS, DFS, and UCS paths
$queries=@('Q1')
foreach($ix in 0..0){
 $r=$ix%5; $c=[math]::Floor($ix/5); $x=$x0+$c*($panelW+24); $y=$y0+$r*($panelH+16)
 $g.DrawRectangle([System.Drawing.Pens]::LightGray,$x,$y,$panelW,$panelH)
 $qid=$queries[$ix]; $m=$metrics | Where-Object query_id -eq $qid | Select-Object -First 1
 $g.DrawString("$qid  $($m.start) → $($m.goal)",$head,$black,$x+10,$y+8)
 $px=$x+16; $py=$y+38; $pw=$panelW-32; $ph=$panelH-68
 # pale geographic grid
 $grid=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(230,235,240),1)
 foreach($lon in -120,-60,0,60,120){$gx=$px+($lon+180)/360*$pw;$g.DrawLine($grid,[single]$gx,[single]$py,[single]$gx,[single]($py+$ph))}
 foreach($lat in -60,0,60){$gy=$py+(90-$lat)/180*$ph;$g.DrawLine($grid,[single]$px,[single]$gy,[single]($px+$pw),[single]$gy)}
 foreach($alg in 'BFS','DFS','UCS'){
  $pts=@($routes | Where-Object { $_.query_id -eq $qid -and $_.algorithm -eq $alg } | Sort-Object {[int]$_.sequence})
  if($pts.Count -gt 1){$coords=[System.Collections.Generic.List[System.Drawing.PointF]]::new(); foreach($p in $pts){$xx=$px+([double]$p.longitude+180)/360*$pw; $yy=$py+(90-[double]$p.latitude)/180*$ph; $coords.Add([System.Drawing.PointF]::new([single]$xx,[single]$yy))}; $pen=switch($alg){'BFS'{$blue};'DFS'{$orange};default{$green}};$g.DrawLines($pen,$coords.ToArray())}
 }
 $g.DrawString('BFS', $small,[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(35,110,210)),$x+12,$y+$panelH-22)
 $g.DrawString('DFS', $small,[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(235,125,35)),$x+70,$y+$panelH-22)
 $g.DrawString('UCS', $small,[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(35,155,95)),$x+130,$y+$panelH-22)
 $grid.Dispose()
}
$g.DrawString('Airport coordinates    Blue: BFS    Orange: DFS    Green: UCS',$font,$black,50,1035)
$bmp.Save((Join-Path $out 'route_comparison.png'),[System.Drawing.Imaging.ImageFormat]::Png)
# Composite screenshot-like evidence image with metrics on left and full chart at right
$shot=[System.Drawing.Bitmap]::new(1800,1000); $sg=[System.Drawing.Graphics]::FromImage($shot);$sg.Clear([System.Drawing.Color]::White)
$sg.DrawString('Lab 1 Results',$title,$black,24,15)
$sg.DrawString('metrics.csv',$head,$black,25,58)
$headers='Query Start Goal Algorithm Hops Distance km Expanded MaxFrontier'
$sg.DrawString($headers,$small,$black,25,85)
$i=0
foreach($m in $metrics){$yy=106+$i*34;$line=('{0,-5} {1,-5} {2,-5} {3,-9} {4,4} {5,12} {6,8} {7,10}' -f $m.query_id,$m.start,$m.goal,$m.algorithm,$m.hops,$m.path_cost_km,$m.expanded,$m.max_frontier);$sg.DrawString($line,$small,$black,25,$yy);$i++}
$sg.DrawString('route_comparison.png',$head,$black,800,58)
$chart=[System.Drawing.Image]::FromFile((Join-Path $out 'route_comparison.png'));$sg.DrawImage($chart,800,85,970,873);$chart.Dispose()
$shot.Save((Join-Path $out 'submission_screenshot.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$sg.Dispose();$shot.Dispose();$g.Dispose();$bmp.Dispose();$font.Dispose();$small.Dispose();$title.Dispose();$head.Dispose();$blue.Dispose();$orange.Dispose();$green.Dispose()
Get-ChildItem $out -File | Select-Object Name,Length
