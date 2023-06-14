import crawler
import asyncio
import timeit

if __name__ == "__main__":
    print("runner")
    t_start = timeit.default_timer()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(crawler.main()) 
    t_stop = timeit.default_timer()

    print("Elapsed time: ", t_stop-t_start)