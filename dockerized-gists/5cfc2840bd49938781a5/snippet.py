def draw_path(self,x,y):

			top_right = 999999999999999999999999999999999999
			top_left =  999999999999999999999999999999999999
			top =       999999999999999999999999999999999999
			if y == 0:
				return
			
			self.writablePixels[y,x] = (255,0,0)
			# print str((x,y))
			if x != len(self.costs) - 1:
				top_right = self.costs[x + 1][y - 1]
			if x != 0:
				top_left = self.costs[x - 1][y - 1]
			top = self.costs[x][y - 1]

			values = [top,top_right,top_left]

			min_index = values.index(min(values))
			if min_index == 0:
				self.draw_path(x,y-1)
			elif min_index == 1:
				self.draw_path(x + 1, y - 1)
			elif min_index == 2:
				self.draw_path(x - 1, y - 1)
