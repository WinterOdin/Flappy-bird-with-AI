import pygame
import random
import time
import os
import neat

pygame.font.init()
WIN_WIDTH  = 512
WIN_HEIGHT = 800

bird_imgs   = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png")))]
pipe_img    = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
bg_img      = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))
base_img    = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))

font        = pygame.font.SysFont('comicsans', 50)



class Bird:
    IMGS         = bird_imgs
    MAX_ROTATION = 20
    ROTATION     = 20
    ANIMATION    = 20

    def __init__(self,x,y):
         self.x         = x
         self.y         = y
         self.tilt      = 0 #titlt
         self.tickCount = 0 #physic
         self.velocity  = 0 
         self.height    = self.y
         self.imgCount  = 0 
         self.img       = self.IMGS[0]
        
    def jump(self):
        self.velocity   = -10.5
        self.tickCount  = 0
        self.height     = self.y

    def move(self):
        self.tickCount  += 1
        displacement     = self.velocity*self.tickCount+1.5*self.tickCount**2

        if displacement >= 16:
            displacement = 16

        if displacement  < 0:
            displacement -= 2
        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION 

#checking what image we need to show based on the aniomation value
    def draw(self, win):
        self.imgCount += 1

        if self.imgCount    < self.ANIMATION:
            self.img = self.IMGS[0]

        elif self.imgCount  < self.ANIMATION*2:
            self.img = self.IMGS[1]

        elif self.imgCount  < self.ANIMATION*3:
            self.img = self.IMGS[2]

        elif self.imgCount  < self.ANIMATION*4:
            self.img = self.IMGS[1]

        elif self.imgCount  == self.ANIMATION*4 + 1:
            self.img = self.IMGS[0]
            self.imgCount = 0 

        if self.tilt        <= -80:
            self.img         = self.IMGS[1]
            self.imgCount    = self.ANIMATION*2
        
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect      = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self,x):
        self.x = x
        self.height     = 0
        self.top        = 0 
        self.bottom     = 0
        self.gap        = 100
        self.pipeTop    = pygame.transform.flip(pipe_img, False, True)
        self.pipeBottom = pipe_img
        self.passed     = False
        self.setHeight()

    def setHeight(self):
        self.height = random.randrange(50,450)
        self.bottom = self.height + self.GAP
        self.top    = self.height - self.pipeTop.get_height()
    
    def move(self):
        self.x -= self.VEL

    def draw(self,win):
        win.blit(self.pipeTop,    (self.x, self.top))
        win.blit(self.pipeBottom, (self.x, self.bottom))
    
    def colide(self,Bird):
        birdMask   = Bird.get_mask()
        topMask    = pygame.mask.from_surface(self.pipeTop)
        bottomMask = pygame.mask.from_surface(self.pipeBottom)

        topOffset     = (self.x - Bird.x, self.top - round(Bird.y))
        bottomOffset  = (self.x - Bird.x, self.bottom - round(Bird.y))

        bPoint = birdMask.overlap(bottomMask,bottomOffset)
        tPoint = birdMask.overlap(topMask,topOffset)

        if bPoint or tPoint:
            return True
        
        return False

class Base:
    VEL     = 5 
    WIDTH   = base_img.get_width()
    IMG     = base_img

    def __init__(self,y):
        self.y  = y
        self.x1 = 0 
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL 

        if self.x1  + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2  + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG,   (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, birds,pipes, base, score):
    win.blit(bg_img, (0,0))


    for pipe in pipes:
        pipe.draw(win)

    text = font.render("SCORE: "+ str(score),1,(255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

def main(genomes, config):

    nets  = []
    ge    = []

    birds = []

    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0 
        ge.append(g)

    base  = Base(730)
    pipes = [Pipe(700)]
    win   = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    run   = True
    score = 0
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipeIndex = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipeTop.get_width():
                pipeIndex = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipeIndex].height), abs(bird.y - pipes[pipeIndex].bottom)))

            if output[0] > 0.5:
                bird.jump()

        addedPipe    = False
        removedPipes = []

        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.colide(bird):
                    ge[x].fitness -= 1 
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    addedPipe   = True
            
            if pipe.x + pipe.pipeTop.get_width() < 0:
                removedPipes.append(pipe)

            pipe.move()

        if addedPipe:

            score += 1
            for x in ge:
                x.fitness += 5
            pipes.append(Pipe(700))

        for x in removedPipes:
            pipes.remove(x)
        
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
                

        base.move()
        draw_window(win, birds, pipes, base, score)



def run(configPath):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, configPath)

    p = neat.Population(config) 
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)
    
if __name__ == '__main__':
    localDir   = os.path.dirname(__file__)
    configPath = os.path.join(localDir, 'config-feedforward.txt')
    run(configPath) 